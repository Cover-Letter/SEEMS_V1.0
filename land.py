'''
Created on May 26, 2015

@author: Liyan Xu; Yufeng Chen
'''
import sys
import dbfread
import arcpy
from arcpy import env
from arcpy.sa import *
class Land(object):
    '''
    The land class
    '''


    def __init__(self, record, VarList, current_year):
        '''
        Construct the land class from the land table in the DB, and then add some other user-defined attributes.

        record - a record in the land table in the DB.       
        VarList - the variable `(or field) list of the land table in the DB
        VarList = {paramName1: paramOrder1, paramName2: paramOrder2, ...}   
        
        '''
        
        # Set the attributes (var) and their values (record) from the land table in the DB.                
        for var in VarList:
            setattr(self, var[0], record[var[1]])

        # Set the current time stamp
        self.StatDate = current_year
        
        # Define the variable indicating if the land is actually farmed
        self.actual_farming = False
        
        # Define the variables related to vegetation succession.
        self.succession_length = 0 # The time length of vegetation succession.
    
        # Define a switch indicating whether the land parcel, if it is farmland, is reverted to forest beginning this year
        self.IsG2G_this_year = False

    def land_step_go(self, society_instance, iteration_count):

        # Update the statistics time stamp
        self.StatDate = society_instance.current_year

        # Deal with the reverted farmland
        try:
            for land in society_instance.hh_dict[self.HID].own_capital_properties.land_properties_list:
                if land.ParcelID == self.ParcelID and land.IsG2G_this_year == True:
                    society_instance.hh_dict[self.HID].own_capital_properties.land_properties_list.remove(land)

                    self.IsG2G_this_year = False
                    self.IsG2G = 1
                    self.SStartyear = society_instance.current_year
                    self.HID = ''

        except:
            pass
            # This try...except session is necessary because some land parcels in the land table 
            # have an HID that does not appear in the household table.
        

        # Then simulate the natural land cover succession process
        self.land_cover_succession(society_instance.current_year, society_instance.model_parameters_dict)

    def land_cover_succession(self, current_year, model_parameters):
        '''
        The natural succession process of land cover.
        '''
        
        # Determine the length of vegetation succession
        if self.SStartyear != 0:
            self.succession_length = current_year - self.SStartyear
            
        
            if self.LandCover == 'Cultivate' and self.IsG2G == 1:
               if self.succession_length == int(model_parameters['CultivatedSuccessionYear']):
                  self.LandCover = 'Shrubbery'
                  self.SStartyear = current_year 
            
            elif self.LandCover == 'Construction' and self.IsC2G == 1:
                if self.succession_length == int(model_parameters['ConstructionSuccessionYear']):
                    self.LandCover = 'Shrubbery'
                    self.SStartyear = current_year        
            
            elif self.LandCover == 'Meadow':
                if self.ClimaxComType == 'Meadow':
                    pass # Do nothing
                elif self.ClimaxComType == 'Bamboo':
                    if self.succession_length == int(model_parameters['GrassSuccessionShrubberyYear']):
                        self.LandCover = 'Bamboo'
                        self.SStartyear = current_year
                else:                
                    if self.succession_length == int(model_parameters['GrassSuccessionShrubberyYear']):
                        self.LandCover = 'Shrubbery'
                        self.SStartyear = current_year
                                
            elif self.LandCover == 'Shrubbery':
                if self.succession_length == int(model_parameters['ShrubberySuccessionYear']):
                    self.LandCover = 'Broad-leaved Forest'
                    self.SStartyear = current_year            
                                   
            elif self.LandCover == 'Broad-leaved Forest':           
                if self.ClimaxComType == 'Mixed Forest' or self.ClimaxComType == 'Coniferous Forest':                                
                    if self.succession_length == int(model_parameters['BroadleavedForestSuccessionYear']):
                        self.LandCover = 'Mixed Forest'
                        self.SStartyear = current_year
                                   
            elif self.LandCover == 'Mixed Forest' :
                if self.ClimaxComType == 'Coniferous Forest':                                
                    if self.succession_length == int(model_parameters['MixedForestSuccessionYear']):
                        self.LandCover = 'Coniferous Forest'
                        self.SStartyear = current_year 
                else:
                      self.LandCover = 'Mixed Forest'
                      self.SStartyear = current_year

    def land_neibourhood(self,iterationcount):

        env.workspace = "C:/WolongRun/Results_Output/linshi"
        arcpy.CheckOutExtension("Spatial")
        # cankao = arcpy.Raster('C:\WolongRun\WolongSEEMSDB.mdb\hid')
        cankao = "hid1.tif"
        dsc = arcpy.Describe(cankao)
        arcpy.env.outputCoordinateSystem = dsc.SpatialReference
        arcpy.env.overwriteOutput = True

        neighborpath = "C:/WolongRun/Results_Output/land/"
        nei_save_year = iterationcount

        # Feature to raster

        InFeatures = "LULC_wl.shp"
        InField = "LCTypeID"
        OutRaster = neighborpath + 'raster' + '_' + str(nei_save_year) + '.tif'
        InCellSize = "30"
        arcpy.gp.FeatureToRaster_conversion(InFeatures, InField, OutRaster, InCellSize)
        inRaster = OutRaster
        reclassField = "Value"
        remap = RemapValue(
            [["1", "NoData"], ["2", "NoData"], ["3", 0], ["4", 1], ["5", 1], ["6", 1], ["7", 1], ["8", 1], ["9", 1],
             ["10", "NoData"], ["11", "NoData"]])
        outReclassify = Reclassify(inRaster, reclassField, remap, "NODATA")
        outReclassify.save(neighborpath + 'reclass' + str(nei_save_year) + '.tif')
        inRaster2 = outReclassify

        # aRaster = arcpy.Raster(neighborpath + 'LULC_wlr'+ '_' + str(iterationcount))
        # bRaster = arcpy.Raster(neighborpath + 'reclass.tif')
        # cRaster = aRaster + bRaster
        # reclassField = "Value"
        # remap = RemapValue(
        #     [["-1", "0"], ["-2", "0"], ["21", 1], ["20", 1]])
        # outRemap = Reclassify(cRaster, reclassField, remap, "NoDaTa")
        # outRemap.save(neighborpath + 'remap'+ '_' + str(nei_save_year) +'.tif')
        # inRaster = outRemap
        neighborhood = NbrRectangle(3, 3, "CELL")
        outFocalStatistics = FocalStatistics(inRaster2, neighborhood, "SUM", "NODATA")
        outFocalStatistics.save(neighborpath + 'outstat' + '_' + str(nei_save_year) + '.tif')
        inRaster3 = outFocalStatistics
        inMaskData = "lupolylin.shp"
        outExtractByMask = ExtractByMask(inRaster3, inMaskData)
        outExtractByMask.save(neighborpath + 'extract' + '_' + str(nei_save_year) + '.tif')
        inZoneData = "LULC_wl.shp"
        zoneField = "HID"
        inValueRaster = outExtractByMask
        outTable = neighborpath + 'zonal' + '_' + str(nei_save_year) + '.dbf'
        ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster,outTable, "NODATA", "ALL")
        # intable = dbfread.DBF(outTable, encoding='GBK')
        #
        # outZonalStats = ZonalStatistics(inZoneData,zoneField,inValueRaster,"MAJORITY",
        #                                 "NODATA")
        # outZonalStats.save(neighborpath + 'outZonal' + '_' + str(nei_save_year) + '.tif')
        # inRaster3 =  outZonalStats
        # outReclass = Reclassify(inRaster3,"Value",RemapRange([[0,6,-2],[6,9,20],["NoData",30]]))
        # outReclass.save( neighborpath + 'LULC_wlr' + '_' + str(iterationcount + 1))
        # outReclassify = Reclassify(inRaster, reclassField, remap, "NODATA")
        # Save the output
        # outReclassify.save(neighborpath + 'reclass' + '_' + str(nei_save_year) + '.tif')
        # Check out the ArcGIS Spatial Analyst extension license
        # Execute FocalStatistics
        # Save the output

        # arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS_1984_UTM_Zone_48N")

        # Set local variables

        # zonal statstics
        # Set environment settings
        # inZoneData = "C:/SEEMS2018Update/SEEMS2018/WolongRun/GIS Resources/all/LULC_wl_all.shp"
        # zoneField = "HID"
        # inValueRaster = arcpy.Raster('C:/SEEMS2018Update/SEEMS2018/WolongRun/OutPut/zonestatout3')
        # arcpy.CheckOutExtension("Spatial")
        # outZonalStatistics = ZonalStatistics(inZoneData, zoneField, inValueRaster,"MAJORITY", "NODATA")
        # outZonalStatistics.save("C:/SEEMS2018Update/SEEMS2018/WolongRun/OutPut/zonal4")

        # Set local variables

        # Check out the ArcGIS Spatial Analyst extension license
        # Execute ZonalStatisticsAsTable

    # InFeatures = "LULC_wl.shp"
    # InField = "LCTypeID"
    # neighborpath = "C:/WolongRun/Results_Output/land/"
    # nei_save_year = current_year
    # OutRaster = neighborpath + 'raster' + '_' + str(nei_save_year) + '.tif'
    # InCellSize = "25"
    # # Process: FeatureToRaster_conversion
    #
    # arcpy.gp.FeatureToRaster_conversion(InFeatures, InField, OutRaster, InCellSize)

    # Set local variables
    #       inRaster = OutRaster

    # reclassField = "Value"
    # remap = RemapValue(
    #     [["1", 1], ["2", 1], ["3", 0], ["4", 1], ["5", 1], ["6", 1], ["7", 1], ["8", 1], ["9", 1], ["10", 1], ["11",1]])
    # Check out the ArcGIS Spatial Analyst extension license
    # Execute Reclassify





        
        