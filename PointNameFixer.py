"""
This program updates point names of as build surveys from csv files.
Author: Edip Ahmet Taskin
24/2022
"""

import tkinter as tk
from tkinter import ttk
import sv_ttk
import glob
import configparser
import pandas as pd
import geopandas as gpd
from pathlib import Path

config = configparser.ConfigParser()
config.read('path.ini')


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create widgets
        self.setup_widgets()

        self.csv_path_input.set(config['path']['csv'])
        self.asbuilt_path_input.set(config['path']['asbuilt'])
        self.output_path_input.set(config['path']['output'])

        # Merge csv files
    def merge_csv( self, dir_path ):
        files = glob.glob( dir_path+"\*.csv", recursive=True )
        column_names = ["Point_Name", "Easting", "Northing", "Elevation", "Point Code"]
        df_from_each_file = (pd.read_csv(f, names=column_names) for f in files)
        df = pd.concat(df_from_each_file, ignore_index=True)
        return df

    # Find as build files
    def find_asbuilts( self, dir_path ):
        dir_path = dir_path + '\*.pts'
        files = glob.glob( dir_path, recursive=True )
        return files

    def process_data(self, asbuilt_path):
        # Update the confg file with the new path variables
        # Update the parameters
        config.set( 'path', 'csv', self.csv_path.get() )
        config.set( 'path', 'asbuilt', self.asbuilt_path.get() )
        config.set( 'path', 'output', self.output_path.get() )
        # Update path.ini file with the new parameters
        with open('path.ini', 'w') as configfile:
            config.write(configfile)
        # Column names for both dataframes
        column_names = ["Point Name", "Easting", "Northing", "Elevation", "Point Code"]
        # Dataframe source paths
        print(self.asbuilt_path.get())
        # self.asbuilt_path.get() is asbuilts path
        print( self.find_asbuilts( self.asbuilt_path.get() ) )
        
        sample_asbuilt = asbuilt_path
        # create dataframes from csv abd pts formats
        df_csv = self.merge_csv( self.csv_path.get() )
        df_asbuilt = pd.read_csv( sample_asbuilt, names=column_names, sep='\t' )
        # greate geopandas from dataframe as point layer with Irish CRS
        gdf_csv = gpd.GeoDataFrame(
        df_csv, geometry=gpd.points_from_xy(df_csv['Easting'], df_csv['Northing']), crs="EPSG:2157")
        gdf_asbuilt = gpd.GeoDataFrame(
        df_asbuilt, geometry=gpd.points_from_xy(df_asbuilt['Easting'], df_asbuilt['Northing']), crs="EPSG:2157")
        # Creating polygon from point layer with buffer (additional info)
        #gdf_asbuilt['geometry'] = gdf_csv.geometry.buffer(0.5)
        # Check if the CRSs are equal for the dataframes
        print(gdf_csv.crs == gdf_asbuilt.crs)
        # Spatial join asbuilt with csv dataframe using inner method
        joindef_asbuilt = gdf_asbuilt.sjoin(gdf_csv, how="left")

        print(joindef_asbuilt.shape[0])

        # file name without extention
        file_name = Path(asbuilt_path).stem

        # export it to gpkg file to see on QGIS
        #joindef_asbuilt.to_file(self.output_path.get() + "\\" + file_name + ".gpkg", driver="GPKG")
        joindef_asbuilt.rename(columns = {'Easting_right':'Easting', 'Northing_right':'Northing', 'Elevation_right':'Elevation', 'Point Code_right':'Point_Code'}, inplace = True)
        joindef_asbuilt = joindef_asbuilt[['Point_Name', 'Easting', 'Northing', 'Elevation', 'Point_Code']].copy()
        
        joindef_asbuilt.to_csv(self.output_path.get() + "\\" + file_name + ".pts", sep='\t', encoding='utf-8', na_rep="", index=False, header=True)

    def asbuilt_output(self):
        asbuilt_list = self.find_asbuilts( self.asbuilt_path.get() )
        for i in asbuilt_list:
            self.process_data( i )

    def folder_path_csv(self):
        folder = tk.filedialog.askdirectory()
        if folder:
            self.csv_path_input.set(folder)

    def folder_path_asbuilt(self):
        folder = tk.filedialog.askdirectory()
        if folder:
            self.asbuilt_path_input.set(folder)

    def folder_path_output(self):
        folder = tk.filedialog.askdirectory()
        if folder:
            self.output_path_input.set(folder)

    def setup_widgets(self):
        # pady is vertical space, padx is horizontal space of the widget.
        # Create a Frame for input widgets
        self.widgets_frame = ttk.LabelFrame(self, text="Select Folders", padding=(10, 10, 10, 10))
        self.widgets_frame.grid(
            row=0, column=1, padx=20, pady=(20), sticky="nsew", rowspan=3
        )
        self.widgets_frame.columnconfigure(index=1, weight=1)
        
        # CSV File Folder
        # Label1
        self.label1 = ttk.Label(self.widgets_frame, text="CSV Folder")
        self.label1.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
        
        # Readonly text1
        self.csv_path_input = tk.StringVar()
        
        self.csv_path = ttk.Entry(self.widgets_frame, textvariable=self.csv_path_input, state=tk.DISABLED)
        self.csv_path.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")
        
        # Button1
        self.button1 = ttk.Button(self.widgets_frame, text="...", command=self.folder_path_csv)
        self.button1.grid(row=1, column=2, padx=5, pady=10, sticky="nsew")
        
        # PVS File Folder
        # Label2
        self.label2 = ttk.Label(self.widgets_frame, text="As-Built Folder")
        self.label2.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")
        
        # Readonly text2
        self.asbuilt_path_input = tk.StringVar()
        self.asbuilt_path = ttk.Entry(self.widgets_frame, textvariable=self.asbuilt_path_input, state=tk.DISABLED)
        self.asbuilt_path.grid(row=2, column=1, padx=5, pady=10, sticky="nsew")

        # Button2
        self.button2 = ttk.Button(self.widgets_frame, text="...", command=self.folder_path_asbuilt)
        self.button2.grid(row=2, column=2, padx=5, pady=10, sticky="nsew")
        
        # Output Folder
        # Label3
        self.label3 = ttk.Label(self.widgets_frame, text="Output Folder")
        self.label3.grid(row=3, column=0, padx=5, pady=10, sticky="nsew")
        
        # Readonly text3
        self.output_path_input = tk.StringVar()
        self.output_path = ttk.Entry(self.widgets_frame, textvariable=self.output_path_input, state=tk.DISABLED)
        self.output_path.grid(row=3, column=1, padx=5, pady=10, sticky="nsew")

        # Button3
        self.button3 = ttk.Button(self.widgets_frame, text="...", command=self.folder_path_output)
        self.button3.grid(row=3, column=2, padx=5, pady=10, sticky="nsew")
        
        # Process Button
        self.button4 = ttk.Button(self.widgets_frame, text="Process", command=self.asbuilt_output)
        self.button4.grid(row=4, column=1, padx=5, pady=10, sticky="nsew")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Point Name Fixer")
    #root.state("zoomed")

    # Simply set the theme
    sv_ttk.set_theme("light")

    app = App(root)
    app.pack(fill="both", expand=True)

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate))

    root.mainloop()
