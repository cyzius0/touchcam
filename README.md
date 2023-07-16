# touchcam 1.0
A single camera and some code try to imitate a touchscreen using monocular depth perception and finger tracking.

### VERSIONS
<details open>
<summary><b>V1 - first demo in python using opencv and mediapipe</b></summary>
  
> last updated: 16/7/2023

★ RELEASE ★
- v1.0 - initial release ⭐wow!⭐ (16/7/2023)

  <img src="https://github.com/cyzius0/single-cam-touchscreen/assets/138211548/0e8474ae-4c31-44de-979f-198395c0e467" alt="v1-demo" width="500">
  
  > v1.0 demo - points are connected with straight lines; some degree of accuracy
  
  - [X] hand tracking module
  - [X] draw best fit line that intersects pointer
  - [X] depth function
  - [X] y-correction function
  - [X] error rejection for mediapipe hand detection
  - [X] error rejection for depth



</details>
<details close>
<summary><b>V2 - increased accuracy and adaptability</b></summary>
  
> last updated: 16/7/2023

✦ DEVELOPMENT ✦
  
  - [ ] pattern detection instead of hand for better accuracy
  - [ ] automatic calibration of finger size
  - [ ] proper canvas
  - [ ] curve generation via points

★ RELEASE ★

</details>

### CONCEPT

<img src="https://github.com/cyzius0/single-cam-touchscreen/assets/138211548/56426d83-9e71-46ff-9786-d229eb5008b1" alt="front-pov" width="700">

> the setup (drawn in Concepts)

<img src="https://github.com/cyzius0/single-cam-touchscreen/assets/138211548/52fd8d1a-34a3-4ec6-a773-bd3adf14a2b3" alt="webcam-pov" width="500">

> camera's POV

#### Footnotes
The depth and y value is mapped from 0-1 and multiplied by the corresponding dimensions (px) of the screen to get the screen's x and y value.
The minimum depth (distance from camera to canvas) and width of the canvas is required. Depth in cm.

A reference size of the finger at minimum depth is required for the 3 lengths between the 4 landmarks and a length from the first to last landmark

The resolution of the camera matters to detect the pattern on the finger and to increase precision.

The accuracy of the points becomes worse further from the camera as a small erroneous change in length can result in a large change in depth. Refer to depth equation. This can be resolved with better tracking.




