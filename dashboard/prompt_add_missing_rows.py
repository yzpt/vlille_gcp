# i got a dataframe with two columns :"paris_timestamp" and "total_velos" and i want to plot the total_velos in function of the paris_timestamp.

# create a script:

# for each row:
#     if next_row['paris_timestamp'] - row['paris_timestamp'] > 1 minute:
#         add a row with the same total_velos and the paris_timestamp + 1 minute
#         do it until the next recorded timestamp

# timestamp are in the format : 2018-01-01 00:00



import pandas as pd
from datetime import datetime, timedelta

# Sample DataFrame with 'paris_timestamp' and 'total_velos' columns
# Replace this with your actual DataFrame
data = {
    'paris_timestamp': ['2018-01-01 00:00', '2018-01-01 00:02', '2018-01-01 00:05'],
    'total_velos': [10, 15, 20]
}

df = pd.DataFrame(data)
df['paris_timestamp'] = pd.to_datetime(df['paris_timestamp'])

# Function to add missing rows with timestamps
def add_missing_rows(df):
    new_rows = []
    for index, row in df.iterrows():
        if index < len(df) - 1:
            next_row = df.iloc[index + 1]
            time_diff = (next_row['paris_timestamp'] - row['paris_timestamp']).total_seconds()
            if time_diff > 60:  # If the time difference is greater than 1 minute
                current_time = row['paris_timestamp']
                while (current_time + timedelta(minutes=1)) < next_row['paris_timestamp']:
                    current_time += timedelta(minutes=1)
                    new_row = {
                        'paris_timestamp': current_time,
                        'total_velos': row['total_velos']
                    }
                    new_rows.append(new_row)
    # Append missing rows to the DataFrame
    df = df.append(pd.DataFrame(new_rows), ignore_index=True)
    # Sort the DataFrame by 'paris_timestamp'
    df = df.sort_values(by='paris_timestamp').reset_index(drop=True)
    return df

# Call the function to add missing rows
df = add_missing_rows(df)

# Plot the data
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(df['paris_timestamp'], df['total_velos'], marker='o')
plt.xlabel('Paris Timestamp')
plt.ylabel('Total Velos')
plt.title('Total Velos vs Paris Timestamp')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
