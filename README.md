# Wisconsin_land_use

- To use land.py, first download land.py, images.zip, and images.db.
- To use this module, you can download land.py.
Then in any enviornment, run import land
c = land.open("images")
c.close()
- Connection has methods list_images, images_year, image_name, image_load, and plot_img.
- c.list_images returns an alphabetically sorted list of images
- c.images_year("area#.npy") returns the year from the DB corresponding to a specific image. 
- c.image_name("area#.npy") returns the name from the DB corresponding to a specific image. 
- c.image_load("area#.npy") returns a numpy area that encodes area usage. 
- c.plot_img("area#.npy", ax=ax) returns a plot like the one below with the image's year and city name.

- Dataset that breaks the US into 30m squares and categorizes show chunks of land have been used from 2001 to 2016 https://www.mrlc.gov/data/nlcd-land-cover-conus-all-years
- Here is how the land is used. https://www.mrlc.gov/data/legends/national-land-cover-database-2016-nlcd2016-legend
- Since the dataset covers the US, however images.db and images.zip cover Wisconsin only.

![](/images/8pm.png)
