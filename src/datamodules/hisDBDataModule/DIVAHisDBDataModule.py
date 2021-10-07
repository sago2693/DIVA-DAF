from pathlib import Path
from typing import Union, List, Optional

from torch.utils.data import DataLoader
from torchvision import transforms

from src.datamodules.base_datamodule import AbstractDatamodule
from src.datamodules.datasets.cropped_hisdb_dataset import CroppedHisDBDataset
from src.datamodules.util.analytics.image_analytics import get_analytics
from src.datamodules.util.misc import validate_path_for_segmentation
from src.datamodules.util.transformations.twin_transforms import TwinRandomCrop, OneHotEncoding, OneHotToPixelLabelling
from src.datamodules.util.transformations.wrapper_transforms import OnlyImage, OnlyTarget
from src.utils import utils

log = utils.get_logger(__name__)


class DIVAHisDBDataModuleCropped(AbstractDatamodule):
    def __init__(self, data_dir: str = None,
                 selection_train: Optional[Union[int, List[str]]] = None,
                 selection_val: Optional[Union[int, List[str]]] = None,
                 selection_test: Optional[Union[int, List[str]]] = None,
                 crop_size: int = 256, num_workers: int = 4, batch_size: int = 8,
                 shuffle: bool = True, drop_last_batch: bool = True):
        super().__init__()

        analytics = get_analytics(input_path=Path(data_dir),
                                  get_gt_data_paths_func=CroppedHisDBDataset.get_gt_data_paths)

        self.mean = analytics['mean']
        self.std = analytics['std']
        self.class_encodings = analytics['class_encodings']
        self.num_classes = len(self.class_encodings)
        self.class_weights = analytics['class_weights']

        self.image_transform = OnlyImage(transforms.Compose([transforms.ToTensor(),
                                                             transforms.Normalize(mean=self.mean, std=self.std)]))
        self.target_transform = OnlyTarget(transforms.Compose([
            # transforms the gt image into a one-hot encoded matrix
            OneHotEncoding(class_encodings=self.class_encodings),
            # transforms the one hot encoding to argmax labels -> for the cross-entropy criterion
            OneHotToPixelLabelling()]))
        self.twin_transform = TwinRandomCrop(crop_size=crop_size)

        self.num_workers = num_workers
        self.batch_size = batch_size

        self.shuffle = shuffle
        self.drop_last_batch = drop_last_batch

        self.data_dir = validate_path_for_segmentation(data_dir)

        self.selection_train = selection_train
        self.selection_val = selection_val
        self.selection_test = selection_test

        self.dims = (3, crop_size, crop_size)

    def setup(self, stage: Optional[str] = None):
        super().setup()
        if stage == 'fit' or stage is None:
            self.train = CroppedHisDBDataset(**self._create_dataset_parameters('train'), selection=self.selection_train)
            self.val = CroppedHisDBDataset(**self._create_dataset_parameters('val'), selection=self.selection_val)

            self._check_min_num_samples(num_samples=len(self.train), data_split='train',
                                        drop_last_batch=self.drop_last_batch)
            self._check_min_num_samples(num_samples=len(self.val), data_split='val',
                                        drop_last_batch=self.drop_last_batch)

        if stage == 'test' or stage is not None:
            self.test = CroppedHisDBDataset(**self._create_dataset_parameters('test'), selection=self.selection_test)
            # self._check_min_num_samples(num_samples=len(self.test), data_split='test',
            #                             drop_last_batch=False)

    def _check_min_num_samples(self, num_samples: int, data_split: str, drop_last_batch: bool):
        num_processes = self.trainer.num_processes
        batch_size = self.batch_size
        if drop_last_batch:
            if num_samples < (self.trainer.num_processes * self.batch_size):
                log.error(
                    f'#samples ({num_samples}) in "{data_split}" smaller than '
                    f'#processes({num_processes}) times batch size ({batch_size}). '
                    f'This only works if drop_last_batch is false!')
                raise ValueError()
        else:
            if num_samples < (self.trainer.num_processes * self.batch_size):
                log.warning(
                    f'#samples ({num_samples}) in "{data_split}" smaller than '
                    f'#processes ({num_processes}) times batch size ({batch_size}). '
                    f'This works due to drop_last_batch=False, however samples will occur multiple times. '
                    f'Check if this behavior is intended!')

    def train_dataloader(self, *args, **kwargs) -> DataLoader:
        return DataLoader(self.train,
                          batch_size=self.batch_size,
                          num_workers=self.num_workers,
                          shuffle=self.shuffle,
                          drop_last=self.drop_last_batch,
                          pin_memory=True)

    def val_dataloader(self, *args, **kwargs) -> Union[DataLoader, List[DataLoader]]:
        return DataLoader(self.val,
                          batch_size=self.batch_size,
                          num_workers=self.num_workers,
                          shuffle=self.shuffle,
                          drop_last=self.drop_last_batch,
                          pin_memory=True)

    def test_dataloader(self, *args, **kwargs) -> Union[DataLoader, List[DataLoader]]:
        return DataLoader(self.test,
                          batch_size=self.batch_size,
                          num_workers=self.num_workers,
                          shuffle=False,
                          drop_last=False,
                          pin_memory=True)

    def _create_dataset_parameters(self, dataset_type: str = 'train'):
        is_test = dataset_type == 'test'
        return {'path': self.data_dir / dataset_type,
                'image_transform': self.image_transform,
                'target_transform': self.target_transform,
                'twin_transform': self.twin_transform,
                'classes': self.class_encodings,
                'is_test': is_test}

    def get_img_name_coordinates(self, index):
        """
        Returns the original filename of the crop and its coordinate based on the index.
        You can just use this during testing!
        :param index:
        :return:
        """
        if not hasattr(self, 'test'):
            raise Exception('This method can just be called during testing')

        return self.test.img_paths_per_page[index][2:]

