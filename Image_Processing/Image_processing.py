
from cv2 import cv2 as cv
import numpy as np
import random
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt

def validFile(filename):
    try:
        f = open(filename)
        f.close()
        return True
    except FileNotFoundError:
        print("Invalid image file") 
    


def problem1(inpImage, darkCo, blendingCo, mode):

    if validFile(inpImage):
        image = cv.imread(inpImage)
    else:
        return 0

    if mode == "s":
        mask = cv.imread('Light_leak_mask.jpg')
    elif mode =='r':
        mask = cv.imread('Rainbow_mask.jpg')
    else:
        print("Invalid mode selected, please choose Standard(s) or Rainbow(r)")
        return 0 

    darkenedImage = np.zeros(image.shape, image.dtype)
    #Darkening Image
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            for c in range(image.shape[2]): 
                darkenedImage[y,x,c] = np.clip(image[y,x,c] - darkCo, 0, 255)
    
    #Creating mask
    kernel = np.ones((blendingCo,blendingCo), np.float32)/(blendingCo**2)
    dst = cv.filter2D(mask, -1, kernel)
    
    #Combining mask and darkened image
    result = cv.add(0.8*darkenedImage, 0.5*dst)
    result = np.clip(result,0,255).astype('uint8')
    

    cv.imshow("Original Image -> Darkened Image -> Light Leak Image",np.hstack((image, darkenedImage, result)))
    cv.waitKey(0)


def problem2(image, blendingCo, mode):
    if validFile(image):
        inpImage = cv.imread(image)
    else:
        return 0
    
    def noise(image,prob):
        output = np.zeros(image.shape,np.uint8)
        xCentre = (image.shape[1])/2
        yCentre = (image.shape[0])/2
        
        

        thres = 1 - prob 
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                currentY = abs(i - xCentre)
                currentX = abs(yCentre - j)
                
            
                noiseStrength = np.sqrt(1 - (currentX/(image.shape[1]/2)))
                print(noiseStrength)
                rand = random.random()
                if rand > noiseStrength:
                    rand2 = random.random()
                    if rand2 < prob:
                        output[i][j] = 0
                    elif rand2 > thres:
                        output[i][j] = 255
                    else:
                        output[i][j] = image[i][j]
        return output



    def blendImage(image, mask):
        return cv.divide(image, 255-mask, scale=256)

    
    grayedImage = cv.cvtColor(inpImage, cv.COLOR_BGR2GRAY)
    grayedImage = cv.cvtColor(grayedImage, cv.COLOR_GRAY2BGR)

    inverseGrayedImage = 255 - grayedImage

    blurredImage = cv.GaussianBlur(inverseGrayedImage,ksize=(45,45), sigmaX=0,sigmaY=0)
    blendedImage = blendImage(grayedImage, blurredImage)

    kernelSize = blendingCo
    diagKernel = np.zeros((kernelSize,kernelSize))

    
    diagKernel[np.diag_indices_from(diagKernel)] = 1
    
    if mode == "coloured":
        for i in range(1,3):
            noiseMask = np.zeros_like(blendedImage[:,:,i])
            noiseMask = noise(noiseMask,0.9)
            blurredMask = cv.filter2D(noiseMask, -1, diagKernel) 
            cv.imshow("Blurred Mask", blurredMask)
            blendedImage[:,:,i] = cv.add(0.7*blendedImage[:,:,i],0.3*blurredMask)
            cv.imshow('Original Image -> Coloured Pencil Image', np.hstack((inpImage, blendedImage)))
        
    elif mode == "monochrome":
        noiseMask = np.zeros_like(blendedImage)
        noiseMask = noise(noiseMask,0.9)
        blurredMask = cv.filter2D(noiseMask, -1, diagKernel) 
        noisedImage = cv.add(0.8*blendedImage,0.2*blurredMask)
        noisedImage = np.clip(noisedImage,0,255).astype('uint8')
        cv.imshow("Original Image -> Pencil Image", np.hstack((inpImage, noisedImage)))
    
    else:
        print("Invalid colour mode")
        return 0
    
    cv.waitKey(0)

def problem3(image, blurringSize):
    if validFile(image):
        inpImage = cv.imread(image)
    else:
        return 0
    
    
    def createLUT(x,y):
        plt.plot(x, y, 'ro', ms = 5)
        sp = UnivariateSpline(x, y)
        xs = np.linspace(0, 255, 50)
        plt.plot(xs, sp(xs), 'g', lw=3)
        return sp(range(256))
    
    def brightenDarkCircles(image):
        xCentre = image.shape[1]/2
        yCentre = image.shape[0]/2
        increaseVLUT = createLUT([0,64,128,200,256],[0,80,150,220,256])

        lxMin, lxMax, rxMin, rxMax = int(0.7*(xCentre)), int(0.9*(xCentre)), int(1.1*(xCentre)), int(1.3*(xCentre))
        yMin, yMax = int(0.8*(yCentre)), int(0.95*(yCentre))

        image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        
        #Left Eye
        for y in range(yMin, yMax):
            for x in range(lxMin, lxMax):
                image[y,x,2] = increaseVLUT[image[y,x,2]]
                
        #right eye       
        for y in range(yMin, yMax):
            for x in range(rxMin, rxMax):
                image[y,x,2] = increaseVLUT[image[y,x,2]]
          
        image = cv.cvtColor(image, cv.COLOR_HSV2BGR) 
        return image



    def warmingFilter(image):
       increaseLUT = createLUT([0,64,128,200,256],[0,70,140,210,256])
       increaseSatLUT = createLUT([0,64,128,200,256],[0,80,150,220,256])
       decreasedLUT = createLUT([0,64,128,192,256],[0,50,110,170,230])
       bC, gC, rC = cv.split(image)
       rC = cv.LUT(rC, increaseLUT).astype(np.uint8)
       bC = cv.LUT(bC, decreasedLUT).astype(np.uint8)
       image = cv.merge((bC,gC,rC))
       cv.imshow("Imagea without saturation", image)

       hChan, sChan, vChan = cv.split(cv.cvtColor(image, cv.COLOR_BGR2HSV))
       sChan = cv.LUT(sChan, increaseSatLUT).astype(np.uint8)
       return cv.cvtColor(cv.merge((hChan, sChan, vChan)), cv.COLOR_HSV2BGR)

    brightenedCircles = brightenDarkCircles(inpImage)
    kernel = np.ones((blurringSize,blurringSize), np.float32)/(blurringSize**2)
    blurredImage = cv.filter2D(brightenedCircles, -1, kernel)
    warmedImage = warmingFilter(blurredImage)
    

   
    
    cv.imshow("Original -> Brightended Dark Circles -> Filtered", np.hstack((inpImage,brightenedCircles, warmedImage)))
    cv.waitKey(0)


def problem4(image, swirlAngle, swirlRadius, interp):
    if validFile(image):
         image = cv.imread(image)
    else:
        return 0
    

    def imageSwirl(image, outImage, swirlAngle, swirlRadius, inter):
        map_x = np.zeros((image.shape[0], image.shape[1]), dtype=np.float32) 
        map_y = np.zeros((image.shape[0], image.shape[1]), dtype=np.float32)
        startX = (image.shape[1])//2
        startY = (image.shape[0])//2
        for x in range (image.shape[0]):
            for y in range(image.shape[1]):
                currentX = x - startX
                currentY = startY - y
                currentDist = np.sqrt((currentX**2)+(currentY**2))
                currentAngle = np.arctan2(currentY, currentX)

                swirlSize = 1 - (currentDist/swirlRadius)
                
                if swirlSize > 0:
                    newAngle =  swirlSize* swirlAngle
                    currentAngle += newAngle
                    currentAngle = currentAngle
                    newX = (np.cos(currentAngle)*currentDist) + startX
                    newY = startY - (np.sin(currentAngle)*currentDist)

                    map_x[x,y] = newY
                    map_y[x,y] = newX
                else: 
                    map_x[x,y] = y
                    map_y[x,y] = x
        if inter == 'bilinear':
            outImage = cv.remap(image, map_x, map_y, cv.INTER_LINEAR)
        elif inter == 'nearest':
            outImage = cv.remap(image, map_x, map_y, cv.INTER_NEAREST)
        return outImage
        
                    

    swirlAngle = np.radians(swirlAngle)
   
    

    #Task 1:

    swirledImage = np.array(image)  
    swirledImage = imageSwirl(image, swirledImage, swirlAngle, swirlRadius, interp)
    cv.imshow("Original Image", image)
    cv.imshow("Swirled Image", swirledImage)

    #Task 2:
    kernel = np.ones((2,2), np.float32)/4
    blurred = cv.filter2D(image,-1,kernel)
    blurredImage = np.array(blurred)

    blurredImage = imageSwirl(blurred, blurredImage, swirlAngle, swirlRadius, interp)
    cv.imshow("Blurred Image", blurredImage)

    #Task 3:
    reversedImage = np.array(swirledImage)
    reversedImage = imageSwirl(swirledImage, reversedImage, -swirlAngle, swirlRadius,interp)
    errorImage = cv.subtract(image,reversedImage)
    cv.imshow("Reversed Image", reversedImage)
    cv.imshow("Error Difference", errorImage)
    cv.waitKey(0)



