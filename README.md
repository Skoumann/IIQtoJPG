# Known bugs
There is a known bug in the ImageSDK with a memory leak and therefore i convert the files in batches of 5 and reset the ImageSDK as a HOTFIX.

# IIQ to JPG Converter

A user-friendly GUI application to convert IIQ image files to JPG format.

![1024 logo](https://github.com/user-attachments/assets/6d3fc981-10cf-4b23-a5fc-c76bdd5df3e2)


## Introduction

The **IIQ to JPG Converter** is a desktop application that allows you convert IIQ (Phase One RAW image files) to the widely supported JPG format. The application provides a simple and intuitive interface on top of the phase one imageSDK.

## Installation

### Prerequisites

- **Operating System**: Windows 10 or later (64-bit).
- **.NET Runtime**: Ensure that the .NET 6.0 Runtime is installed. If not, download it from [Microsoft's official website](https://dotnet.microsoft.com/download/dotnet/6.0/runtime).

### Download and Install

1. **Download the Installer**

   - Get the latest version of the installer from the [Releases](https://github.com/Skoumann/IIQtoJPG/releases) page.

2. **Run the Installer**

   - Double-click the `IIQtoJPG_Converter_Setup.exe` file.
   - Follow the on-screen instructions to complete the installation.

3. **Launch the Application**

   - After installation, you can launch the application from the Start Menu or by double-clicking the desktop icon if you chose to create one during installation.

## Usage

![2024-10-08_16-09-16](https://github.com/user-attachments/assets/74e9117d-f879-4302-a9a5-13891e53353e)

1. **Open the Application**

   - Launch **IIQ to JPG Converter** from the Start Menu or desktop shortcut.

2. **Select Input Folder**

   - Click on the **Browse** button next to the **Input Folder** field.
   - Navigate to the folder containing your IIQ files and select it.

3. **Select Output Folder**

   - Click on the **Browse** button next to the **Output Folder** field.
   - Choose the destination folder where you want the JPG files to be saved.

4. **Start Conversion**

   - Click on the **Start Conversion** button.
   - The progress bar will display the conversion progress.
   - A message box will notify you upon completion.



## License

This project is licensed under the MIT License.
Acknowledgments

  - PyInstaller: For packaging the Python application into an executable.
  - Inno Setup: For creating a professional installer for Windows.
  - PyQt5: For the graphical user interface components.
  - Contributors: Thanks to everyone who has contributed to this project.


Note: This application utilizes an external executable (imageSDK4023.exe) for converting IIQ files to JPG. Ensure that all dependencies are correctly installed and that you have the rights to use any third-party tools included.

