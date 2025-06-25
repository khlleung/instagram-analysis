import pandas as pd
import csv
import numpy as np
from glob import glob
from datetime import datetime
from dateutil import tz
import pytz

# Data Extraction
file_names = glob('data/*.csv')
print(file_names)

account_details_df = pd.read_csv([file-path])
daily_account_insights_df = pd.read_csv([file-path])
post_name_list_df = pd.read_csv([file-path])
post_list_df = pd.read_csv([file-path])
post_insights_df = pd.read_csv([file-path])
post_data_df = post_list_df.merge(post_insights_df, on=["post_id"], how='outer').sort_values(['retrieved_time','timestamp'], ascending=False)

# DATA PREPARATION - ACCOUNT INSIGHTS
# Creating Derived Columns
account_details_df['date'] = pd.to_datetime(account_details_df['retrieved_time']).dt.date.astype('datetime64[ns]')
daily_account_insights_df['date'] = pd.to_datetime(daily_account_insights_df['retrieved_time']).dt.date.astype('datetime64[ns]')

# Handling Missing Dates
latest_date = account_details_df['date'].max()
date_index = pd.date_range(start = account_details_df['date'].min(), 
                      end = latest_date, freq='D')
interp_post_values = np.interp(date_index, account_details_df['date'], account_details_df['num_posts']).astype(int)
interp_follower_values = np.interp(date_index, account_details_df['date'], account_details_df['num_followers']).astype(int)
interp_follow_values = np.interp(date_index, account_details_df['date'], account_details_df['num_follows']).astype(int)
interp_reach_values = np.interp(date_index, daily_account_insights_df['date'], daily_account_insights_df['reach']).astype(int)
account_insights_df = pd.DataFrame({'num_posts': interp_post_values, 'num_follows': interp_follow_values, 'num_followers': interp_follower_values, 'reach': interp_reach_values}, index = date_index).sort_index(ascending=False)
account_insights_df.index.name = 'date'

# Creating Derived Columns
account_insights_df['daily_net_followers'] = account_insights_df['num_followers'].diff(-1).fillna(0.0).astype(int)
#print(account_insights_df)

# Save Dataframe as .csv
file_path = [file-path]
with open(file_path, 'w', newline='') as csvfile:
    account_insights_df.to_csv(csvfile)

# DATA PREPARATION - POST LATEST DETAILS
# Re-format posting date and time
post_list_df['posting_datetime_utc'] = list(map(lambda x: datetime.strptime(x,"%Y-%m-%dT%H:%M:%S+0000"), post_list_df['timestamp']))
post_list_df['posting_datetime_hkt'] = list(map(lambda x: x.replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Hong_Kong')), post_list_df['posting_datetime_utc']))
post_list_df['posting_date'] = post_list_df['posting_datetime_hkt'].dt.date
post_list_df['posting_time'] = post_list_df['posting_datetime_hkt'].dt.time
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
post_list_df['posting_weekday'] = list(map(lambda x: weekdays[x.weekday()], post_list_df['posting_date']))

post_name_list_df['posting_date'] = list(map(lambda x: datetime.strptime(x,"%Y-%m-%d").date(), post_name_list_df['posting_date']))


posts_latest_insights_df = post_list_df[['post_id','media_type','posting_date','posting_weekday','posting_time']].copy()
posts_latest_insights_df = posts_latest_insights_df.merge(post_name_list_df, on=['post_id','posting_date','media_type'], how='left')

post_insights_df['retrieved_date'] = list(map(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f").date(), post_insights_df['retrieved_time']))
posts_latest_df = post_insights_df.loc[post_insights_df['retrieved_date'] == latest_date.date()]
posts_latest_insights_df = posts_latest_insights_df.merge(posts_latest_df, on=['post_id'], how='left')
posts_latest_insights_df = posts_latest_insights_df.drop(['retrieved_date', 'retrieved_time'], axis=1)
posts_latest_insights_df[['profile_visits','reels_avg_watch_time (ms)','reels_total_watch_time (ms)']] = posts_latest_insights_df[['profile_visits','reels_avg_watch_time (ms)','reels_total_watch_time (ms)']].fillna(-1).apply(np.int64)
posts_latest_insights_df = posts_latest_insights_df.set_index('post_id')
#print(posts_latest_insights_df.iloc[0])

# Save Dataframe as .csv
file_path = [file-path]
with open(file_path, 'w', newline='') as csvfile:
    posts_latest_insights_df.to_csv(csvfile)

# DATA EXPLORATION
# Content type comparison
latest_content_perf = posts_latest_insights_df.groupby('media_type').agg({
    'likes': 'median',
    'comments': 'median',
    'shares': 'median',
    'saved': 'median',
    'reach': 'median',
    'views': 'median'
})
print(latest_content_perf)
