# Tumor detection in MRI scans
Annabelle Sauve  
101080402

### Running the project
#### Dependencies
Ensure the following Python libraries are installed:
- NumPy
- OpenCV

#### How to run locally
cd into the project directory  
run `tumor_detector.py` with python  
press any key (on the image) to skip to the next one

### Summary
The aim of this project is to use computer vision concepts to create a program that detects tumors in MRI brain scans. I will be implementing methods from “MRI image analysis methods and applications: an algorithmic perspective using brain tumors as an exemplar” by Vadmal & al. (2020)

### Background
This project is inspired by Vadmal & al.’s paper (1)  on magnetic resonance imaging (MRI) image analysis. In this paper, they describe a method that is used to analyse these scans in hopes of finding brain tumors automatically. The paper divides this process into three steps: preprocessing, segmentation, and feature extraction. The authors did not include any source code, but I will be following the text and implementing their method on my own using OpenCV.

### The Challenge / Goals and Deliverables
This problem is challenging because the brain is a very complex organ, and it can be difficult to analyse solely by looking at images without the help of computer vision algorithms. Over the course of this project I am hoping to learn more about how medical image analysis works and specifically how it is applied to brain imaging. My background in cognitive science and neuroscience will also be useful when it comes to verifying the results of the code.
I believe this project is complex enough as it requires lots of image manipulation before getting results. With this said, I plan to be able to feed an MRI scan to the code and have it find an anomaly, i.e. tumor, in the image. If everything goes smoothly, I hope to add some lines of code that will give concrete information about the anomaly, such as location or brain structure it is affecting. Success will be evaluated by how precise the code is in finding the tumors in the images and this could be showed with post-analysis diagrams that clearly identify the anomalies. With the help of Vadmal & al.’s paper, I believe this project is realistic for the timeline given. This is also a subject I am very interested in and am prepared to put in extra work if necessary.

### Schedule

|Week | Goal |
|---|---|
|February 7 - 13 | **Data preparation**: Collect MRI images to create a dataset. Write functions to import this data into the program. |
|February 14 - 20| **Preprocessing:** - Remove image noise  - Normalize the images to remove contrast differences - Skull stripping. Remove non useful data (skull, skin, etc.) from the image. Implemented a skull stripping function. Also used simple openCV denoising function. |
| February 20 - 27 | **Preprocessing, bias correction:** Magnetic fields create intensity variations in the images and this must be corrected. The paper proposes four different methods: filtering, surface fitting, segmentation, histogram. Explore them and determine which one is the best for this project. After some tests I have decided to use histograms to do the bias correction. I first calculate a histogram for the image, then clip it at 3% (after some testing, determined that this was the best value). Afterwards I compute the minimum and maximum gray values from the histogram and using those I can then calculate new gain and bias values to adjust the brightness and contrast. I tried sharpening the image using a filter but later found out that this was making the tumors harder to detect (so this is not included). |
| February 28 - March 6 | **Image registration:** This step is needed to align the different images so that the brain structures are at the same location in each image. The paper proposes different techniques to do this. I have not been successful in implementing this. I have however found a way to go around this and still be able to locate the tumors with an atlas. |
| March 7 - 13| **Segmentation:** Divide an image into separate texture layers to identify the tumor. I used a Tozero threshold (thresholding pixels from 125-255) to separate the shapes in the image. This type of threshold is the best since it is more precise than a binary threshold and keeps some of the details. Then I colored the sections and used different intensities to represent the sections. Although not perfect, it gives a very good indication of structures that stand out from the rest. During this step I found that how well the thresholding worked depends on the quality of the original image (quality as in how easy it was to distinguish the structures). Some definitively worked better than others. |
| March 14 - 20| **Segmentation, cont.:** This will be a long task, so I am planning out two weeks to get this done. |
| March 21 - 27| **Feature extraction:** Feature extraction will provide information about the data that was found during the segmentation steps. To find the tumor I first used a closing function with a 10x5 kernel, followed by erosion and dilation to remove additional noise. Then, I applied the built in canny edge detector and from there used a function to find the contours. The maximum contour is assumed to be the tumor. It is then added on the image using a draw contour function. |
| March 28 - April 3| **Testing and debugging:** Test the program using different images from the data preparation step and debug if necessary. Have concrete results by March 31. |
| April 4 - 10| Add in code that presents the data nicely and any other final touches. Prepare for submission & presentation. |
| April 11 - 14| Submit in time for April 14th deadline.|

### Data
The data that is used in this project was obtained from various sources. Images named 1 - 7 are from The National Library of Medicine's _MedPix_ database (2). Images named 8 - 16 are from the _Science Photo Library_ database (3). All of the images are axial sections (view from the top the head).

### Files
**tumor_detector.py** - Tumor detector program  
**/data/** - Folder containing the images used in the program.

### References
(1) Vadmal, V., Junno, G., Badve, C., Huang, W., Waite, K. A., Barnholtz-Sloan, J. S. (2020, April). MRI image analysis methods and applications: an algorithmic perspective using brain tumors as an exemplar. _Neuro-Oncology Advances_, 2(1). https://doi.org/10.1093/noajnl/vdaa049  
(2) https://medpix.nlm.nih.gov/home  
(3) https://www.sciencephoto.com/
