from torch.utils.data import Dataset
from os import listdir, path
from tqdm import tqdm
import cv2
import numpy as np

class YOLODataset(Dataset):
    def __init__(self, path, transform=None, all_label=None):
        self.path = path
        self.all_label = all_label
        self.data = self.load_data()
        self.transform = transform

    def load_data(self):
        # Load data from path
        data = []

        # path/images
        images_path = path.join(self.path, 'images')
        images = listdir(images_path)

        # path/labels
        labels_path = path.join(self.path, 'labels')

        for filename in tqdm(images, desc='Loading data...'):
            #get image path
            image_path = path.join(images_path, filename)

            #get label path
            terms = filename.split('.')
            terms.pop()
            name = '.'.join(terms)
            label_name = name + '.txt'
            label_path = path.join(labels_path, label_name)

            #open label file
            with open(label_path, 'r') as file:
                label_contents = file.read().strip()

            boxes = []
            labels = []
            for line in label_contents.split('\n'):
                label_terms = line.split(' ')
                label = int(label_terms.pop(0))
                if self.all_label is not None:
                    label = self.all_label
                bounding_box = [float(term) for term in label_terms]
                boxes.append(bounding_box)
                labels.append(label)
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            #convert boxes to np array
            boxes = np.array(boxes)

            data.append(
                {
                    'image': img,
                    'boxes': boxes,
                    'labels': labels
                }
            )

        
        return data


    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        
        if self.transform:
            return self.transform(self.data[idx])
        else:
            return self.data[idx]

