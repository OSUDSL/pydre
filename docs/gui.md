# pydre GUI

The GUI for pydre allows users to visually interface with and run the pydre application. 

To run the GUI:

-   Navigate to the pydre directory (NOT the GUI directory)
-   Command Line Syntax: `python python_gui.py`
-   If missing libraries run: `pip install -r requirements.txt`

## Start Page

Below is a Screenshot of the Start Page for pydre GUI

![Start Page](images/start.JPG)

First the user will need to select a project file from either the list of project files under
the recent files heading or the user can make a new project file/select an existing project file from a 
specified file path by clicking the Open Project file button. 

Select the speedbump2_AAM.json project file under the recent files heading as an example shown below

![Start Page Project Selection Example](images/gui1.JPG)

## Editor Page: Project File Configurations

Below is a Screenshot of the Editor Page on the pydre GUI

![Editor Page Example](images/editor_page.JPG)

-  Filters: Add as many filters by clicking the New Filter button at the right and specify the
    function name to be called in pydre as well as any additional paramters under the dropdown for the filter.
    See Example Below to View the smoothGazeData filter for speedbump2_AAM

    ![Filter Example](images/filter.JPG)

-  Metrics: Similarly Add as many data metrics by clicking the New Metric button at the right and specify the
    fuction name to be called in pydre as well as any additionaly parameters under the dropdown for the metric.
    See Example Below to View the speedbumpHondaGaze2 Metric for speedbump2_AAM

    ![Metric Example](images/metrics.JPG)

-  Rois: Similarly use the New Roi button to specify the Roi and include a path to the csv file under the dropdown
    for any spatial/temporal Roi and include the column name for a column Roi.
    See Example Below to View the column Roi for speedbump2_AAM

    ![Roi Example](images/roi.JPG)

Additional button features are available at the right in order to delete any filters, metrics, and Roi as well as
moving any specified filters, metrics, and Roi up and down on the gui. 
See Screenshot Below for help locating these button features.

![Header Tabs](images/additional_buttons.JPG)

Use the File tab at the top of the gui to open additional project files and save changes when needed.

Use the Edit Tab at the top of the gui to undo or make any additional changes. 

See Screenshot below for help locating these tabs

![Header Tabs](images/Header_tags.JPG)

## Run Pydre Application Page

After specifying the project file configurations users can select the Run Tab at the top of the 
gui and click the Run '"your project name"' dropdown to enter the Run Configurations Page
on the gui. See screenshot below for help locating this dropdown.

![Run Header Example](images/run_button.JPG)

Below is a Screenshot of the Run Page on the GUI.
![Run Page Example](images/run.JPG)

Then, inside the Run Configurations page on the gui, click the Add file button to include the raw data (.dat)
files that are going to be processed by pydre. Then specify an output csv file name in the text area below the
Output File heading or the default out.csv name for the output file will be used. See Screnshot Below
for help locating these areas on Gui.

![Add data file example](images/add_file.JPG)


Finally, select the Run button to run the pydre application and view the Log output below the 
Log tab. The Logs can also be viewed by selecting the Log option under the View Tab at the top of the gui.
Select the Cancel button on the page if needed to go back to the editor project configuration page on gui. 
See Screnshot Below for help locating these areas on Gui.

![Run Pydre example](images/run_pydre.JPG)

## gui/app.py
Starts and Lanches the GUI application with default configuration settings

## gui/config.py
Updates the config file with any changes stored in the config variable

## gui/customs.py
Includes Widget Functionality for Metrics, Filters, Rois, and all other Project Editing Widgets

## gui/handlers.py
Mediates Pydre Functionality accessed by GUI. Run method runs PyDre conversion and saves the resulting output file

## gui/logger.py
Contains logging output information

## gui/popups.py
Contains PopUp messages information

## gui/templates.py
Configures window UI, icon, and title if given

## gui/windows.py
Handles all tasks related to the main window configurations and functionality
