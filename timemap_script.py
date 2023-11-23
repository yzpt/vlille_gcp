import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import imageio

df = pd.read_csv('dataset_light_2023_09_27.csv')
df.dropna(inplace=True)
df['time_index'] = df['record_timestamp'].apply(lambda x: pd.to_datetime(x).to_pydatetime().strftime('%H%M'))
distincts_time_index = df['time_index'].unique()
distincts_time_index.sort()
# set time_index as index
df.set_index('time_index', inplace=True)

folder_path = 'data_23_09_27/'
for time_index in distincts_time_index:
    df_time_index = df.loc[time_index]
    df_time_index.to_csv(folder_path + time_index + '.csv')

# Get the list of files in the "data" folder
file_list = os.listdir(folder_path)
file_list.sort()

# Loop through each file in the folder to generate the figures
for file_name in file_list:
    # Construct the file path
    file_path = os.path.join(folder_path, file_name)
    
    # Read the file into a dataframe
    df = pd.read_csv(file_path)

    # remove line with ratio == null
    df = df[df['ratio'].notna()]

    fig = px.scatter_mapbox(
        df, 
        lat="latitude", 
        lon="longitude",
        size="nb_velos_dispo",
        size_max=40,
        zoom=12, 
        height=400,
        width=400,
        center={"lat": 50.63237, "lon": 3.05816}
    )

    fig.update_layout(mapbox_style="open-street-map")    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_coloraxes(showscale=False)

    # Add file name on top left of the large-sized figure
    fig.add_annotation(
        x=0.07,
        y=0.88,
        xref="paper",
        yref="paper",
        text=file_name[:2] + ':' + file_name[2:4],
        showarrow=False,
        font=dict(size=50)
    )
    
    # Save figure to PNGsize_max=40
    pio.write_image(fig, folder_path + file_name[:-4] +'.png')


# MP4 conversion
initial_files = os.listdir(folder_path)
images = sorted([img for img in os.listdir(folder_path) if img.endswith(".png")])
image_files = [imageio.imread(folder_path + '/' + img) for img in images]

imageio.mimsave('timemap.mp4', image_files, fps=24) 
