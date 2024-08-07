# ImageFolderSplitter
Image Folder Splitter is an application designed to help users efficiently manage and organize large collections of images within a directory.

![grafik](https://github.com/user-attachments/assets/90c59d5b-b486-44ab-b7f5-e21078e67118)

This app enables users to numerically rename their images in the format [XXX-name] and organize them into batches. Users can specify a maximum batch size in megabytes, 
and the app will automatically create and name folders based on the batch size.
Additionally, the application identifies and moves non-image files into a dedicated folder named "non_images," ensuring that the image folders remain clean and focused on images only.
After processing, the app adds a .processed flag file to the root directory to indicate that the images have been processed. This helps prevent re-processing of the same directory.

![grafik](https://github.com/user-attachments/assets/5664f2fd-57f3-46c7-8c3b-13cf65cfcd8c)



This App is currently in german. Depending on demand I'll translate this app.

## Edit suffixes in the sourcecode to your Use-Case
This app is not limited to only images but can work with any suffixes!

![grafik](https://github.com/user-attachments/assets/5c2c709e-21c7-4e50-830a-7cab309f1ba1)



## How to use
1. Download ImageFolderSplitter.py
2. Execute the file using your IDE or terminal
3. Select your desired folder
4. Set Batchsize or toggle "Rename Images" and "Create Batches"
5. Start

Note: I have tried compiling this file into an .exe but I can't seem to get pyinstaller working and auto-py-to-exe creates an .exe which misses imports.
If someone manages to make it work please contact me.

## Check the sourcecode
Feel free to check the sourcecode and report any issues you may find. I am happy to learn from my mistakes



