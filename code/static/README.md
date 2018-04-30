Using static
---------

Want to use a file which is unchanging? Perhaps it's media content or perhaps
it's some static css / js files? Then place the files in here and then
reference it in your code like this:
`url_for('static', filename='style.css')`


Using icons (as fonts!)
---------

If you want to do that, then you need not do much! I've imported and locally installed 
Google's fancy new Material Design iconfonts (link: https://material.io/icons/). The
way to use it is quite simple. Just look at the webpage and start find the icon for you,
then run place it in the markup like this: 
```
<!-- modern browsers -->
<i class="material-icons">3d_rotation</i>
<!-- IE, lol -->
<i class="material-icons">&#xE84D;</i>
```
replacing 3d rotations with the correct icon for you. Then get the right hex value for IE,
too.