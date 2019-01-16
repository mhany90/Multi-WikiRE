import argparse
import logging
import os

import pandas as pd
from tqdm import tqdm

try:
    # Prefer a more specific path.
    from maluuba.newsqa.data_processing import NewsQaDataset
except:
    from data_processing import NewsQaDataset

logging.basicConfig(level=logging.INFO)

dir_name = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(dir_name))
default_dataset_path = os.path.join(project_root, 'combined-newsqa-data-v1.csv')
default_output_dir = os.path.join(dir_name, 'split-data-nil')

parser = argparse.ArgumentParser()
parser.add_argument('--dataset_path', default=default_dataset_path,
                    help="The path to the dataset to split. Default: %s" % default_dataset_path)
parser.add_argument('--output_dir', default=default_output_dir,
                    help="The path folder to put the split up data. Default: %s"
                         % default_output_dir)
args = parser.parse_args()

original = NewsQaDataset.load_combined(args.dataset_path)

logging.info("Loading story ID's split.")
train_story_ids = set(pd.read_csv(os.path.join(dir_name, 'train_story_ids.csv'))['story_id'].values)
dev_story_ids = set(pd.read_csv(os.path.join(dir_name, 'dev_story_ids.csv'))['story_id'].values)
test_story_ids = set(pd.read_csv(os.path.join(dir_name, 'test_story_ids.csv'))['story_id'].values)

train_data = []
dev_data = []
test_data = []
nil_data = []
nil_train = []
nil_dev = []
nil_test = []

nilcount = 0
for row in tqdm(original.itertuples(), total=len(original),
                mininterval=2, unit_scale=True, unit=" questions",
                desc="Splitting data"):
    story_id = row.story_id

    # Filter out when no answer was picked because these weren't used in the original paper.
    answer_char_ranges = row.answer_char_ranges.split('|')
    none_count = answer_char_ranges.count('None')
    if none_count == len(answer_char_ranges):
        nil_data.append(row)
        nilcount += 1
        if story_id in train_story_ids:
            nil_train.append(row)
        if story_id in dev_story_ids:
            nil_dev.append(row)
        if story_id in test_story_ids:
            nil_test.append(row)
        continue
    if story_id in train_story_ids:
        train_data.append(row)
    elif story_id in dev_story_ids:
        dev_data.append(row)
    elif story_id in test_story_ids:
        test_data.append(row)
    else:
        logging.warning(
            "%s is not in train, dev, nor test", story_id)

#print nil_data[0]
#print train_data[0]
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)


def _write_to_csv(data, path):
    pd.DataFrame(data=data).to_csv(path,
                                   columns=original.columns.values,
                                   index=False, encoding='utf-8')


logging.info("Writing split data to %s", args.output_dir)
logging.info("Number of nil questions %d", nilcount)
_write_to_csv(nil_train, os.path.join(args.output_dir, 'nil_train.csv'))
_write_to_csv(nil_dev, os.path.join(args.output_dir, 'nil_dev.csv.test'))
_write_to_csv(nil_test, os.path.join(args.output_dir, 'nil_test.csv'))
_write_to_csv(nil_data, os.path.join(args.output_dir, 'nil.csv'))

