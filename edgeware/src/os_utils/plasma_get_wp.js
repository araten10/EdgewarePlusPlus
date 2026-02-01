let desktop = desktops()[0];
desktop.wallpaperPlugin = "org.kde.image";
desktop.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
print(desktop.readConfig("Image"));
