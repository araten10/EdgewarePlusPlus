# Edgeware++
![Edgeware++ running on Windows 11](screenshots/demo.png)
## What is Edgeware?

Going to say immediately: **Edgeware is not a virus, nor does it install itself onto your computer**. All it installs onto your computer by default is python 3.12 and a few extra libraries, which is needed for it to run. Edgeware **can** potentially modify files on your computer, including deleting or replacing things, but these are all *user set* settings that are not on by default. That being said, other people can download Edgeware, modify it to be malicious, and upload it elsewhere, so exercise caution when downloading versions from other sites. This project is open source, so feel free to peruse the source code if you're unsure.

Now, that all is pretty alarming stuff and seems a bit weird to preface the basic explanation with, but i'm fully aware the name "Edgeware" doesn't inspire the most confidence for a program to be safe.

Edgeware is a fetish-designed program (so 18+ only!!!) that essentially spawns popups over your screen in many different ways. These popups can include images, videos, audio, prompts (a sentence you have to repeat, think writing lines on a blackboard), etc. It's also highly customizable, with the ability to download "packs" people have made and use them yourself. Originally inspired by "Elsaware" (which, truthfully, I know nothing about), the original Edgeware's goal was to be a "fake virus" program that looked like your computer was being taken over by porn. It can be ended at any time and also scheduled in ways to be used more passively. Even if you're not into "gooning" (having a kink for porn addiction/edging for a long time) I feel like Edgeware is a pretty fun and interesting porn delivery system that allows you to see multiple images and videos at once without having to touch your keyboard or mouse.

PetitTournesol (Edgeware's original creator) more or less took a hiatus and hasn't updated Edgeware since 2022, which is totally valid. That being said, I felt like there were lots of things I personally wanted to see in the program. Inspired mostly by being mildly frustrated at deleting those dang desktop icons every time, I decided to start learning python and share the changes i've made. Thus Edgeware++ was born, and as of writing this "new and improved" intro, there's over 30 new features to play around with. Some are quality of life updates, some are more fun things to tease yourself with. I'm generally trying to be as minimally intrusive to the original program as possible- my goal is complete both-ways pack compatibility with the old version of Edgeware. I also don't want to remove any features (unless they were literally defunct), but I have moved some stuff around in the config menu to try and make more space.

## Usage Instructions

"So how do I start using this darn thing?" Click the big ol' "code" button in the top right, then "download zip". Save and extract it somewhere, then run `edgeware/EdgewareSetup.bat`. This will install python 3.12 for you, if you don't already have it. After that it will give you instructions for further use, and open up `edgeware/config.pyw`.

**If you're using Linux**, first you need to install Python 3.12, pip, and mpv yourself, if you don't already have them installed already. Your distribution should contain packages for them. For example, on Debian and its derivatives, you can install them by running `sudo apt install python3 python3-pip mpv`. Once installed, download and extract Edgeware as a ZIP or clone the repository, then run `setup.sh` in a terminal window in the `edgeware` directory. This will create a Python virtual environment for Edgeware, install the dependencies, and create scripts for running Edgeware. `config.sh` allows you to configure Edgeware and `edgeware.sh` will start Edgeware itself. **Please note that my primary OS is windows!** I have gotten endless help from LewdDevelopment, who also used some [pre-existing code from a old Edgeware pull request](https://github.com/PetitTournesol/Edgeware/pull/41) to help make it happen. So if any bugs on Linux start from my own incompetence, I will consult with them and try to fix it- but know that I will not know until people tell me or them!

From there you'll need an actual pack, which can be downloaded online or made yourself. Unfortunately at the time of writing there's really no congregated directory of packs everyone's made, they're all scattered to the four winds... but for a start [the original Edgeware page](https://github.com/PetitTournesol/Edgeware) has a few sample packs, and i'm hoping to make a few myself to showcase the new features this extension can do.

Any time Edgeware has a major update, it might be a good idea to run `EdgewareSetup.bat` again, as this is the file that downloads dependencies for the program.

**Any damage you do to your computer with Edgeware is your own responsibility! Please read the "About" tab in the config window and make backups if you're planning on using the advanced, dangerous settings!**

We have also added a Pack Editor included with each copy of Edgeware++. It's a bit different if you're familiar with the old one- it runs in command line and has different features.

## New Features In Edgeware++:

•*Toggle that switches from antialiasing to lanczos, if Edgeware wasn't displaying popups for you this will fix that! (probably)*

•*Videos and GIFs are played with mpv, which not only loads faster but also should fix audio issues*

•*Toggle to enable/disable desktop icon generation*

•*Ability to cap audio/video popups if so desired, audio was previously limited to 1 and videos were uncapped*

•*Subliminals now have a % chance slider, and can also be capped*

•*Can now change startup graphic and icon per pack, defaults are used if not included*

•*Added feature to ask you to confirm before saving if there are any settings enabled that could be "potentially dangerous", for those of you like me who initially wondered if edgeware would fuck up their computer*

•*Hover tooltips everywhere to help new users get a grasp on things without having to weed through documentation*

•*Edgeware installation now actually readable and gives info on first steps*

•*Toggle that allows you to close a popup by clicking anywhere on it*

•*Import/Export buttons are now in full view at all times at the bottom of the window*

•*Brand shiny new "Pack Info" tab that gives stats and information on the currently loaded pack*

•*Simplified error console in the advanced tab, which could potentially help bugfix some things*

•*Packs now support an "info.json" file which gives people basic information about the pack in the config window*

•*Overhaul to hibernate mode which allows you to choose between multiple different types, and have your wallpaper go back to normal after you close all the popups*

•*File tab that allows you to do basic file management functions*

•*Adding functionality to moods, allowing you to toggle them off/on*

•*"Single Mode", allowing only one popup to spawn per popup roll, making for a more consistent experience if desired*

•*Different graphical themes, including dark mode (and a few other fun ones!)*

•*Allowing creation of a per-pack config setup, to help pack creators show off their "intended" settings*

•*Moving Popups, which bounce around the screen [like some other infamous programs](https://www.youtube.com/watch?v=LSgk7ctw1HY)*

•*Subliminal Message popups, which use the captions file to flash short mantras up randomly*

•*Experimental Linux support that may or may not break in the future (read the section above!)*

•*Complete overhaul to the configuration window UI to make it easier to use*

•*User friendly way to change default images, such as splash screens or icons*

•*Speaking of default images, the splash screen and icons have been changed to shiny new ones! (why? answer is below in the FAQ!)*

•*Backend has been rewritten and simplified for easier developer editing*

•*Booru downloader has been updated*

•*Replace Images now saves backups of images replaced*

•*A new type of popup which taps into your OS's notification feature*

•*Can save multiple packs at once for fast switching between them*

## Planned Additions

Planned additions, as well as currently known issues, can now be found on the [issues page](https://github.com/araten10/EdgewarePlusPlus/issues).

## Packs

For most of these packs, we will include a pack config file so you're able to easily test relevant settings. To apply these settings, you can go into the "File" tab once you've imported the pack, and press the "Load Pack Configuration" button. Once they've been loaded, you're free to take a look around and change anything you see fit, as the packs usually will only change a few settings. Make sure you save before you exit!

Reminder: Check out the "Pack Info" tab for more information on these packs once you download them~

[**Edgeware++ Test Pack**](https://mega.nz/file/VbsEmbLD#gCLx6Ftv161oT7u3yiU8altS07QSElTz-Xo9kRmcugM)
**Version: 2** *[17MB]*
The original test pack for Edgeware++! It's fairly old, and i'm not sure how much i'll be updating it in the future. However, it's completely SFW, has examples for most features up to version ~13, and is extremely small in the filesize department. This is a good place to start if you just want to test running Edgeware, or learn how to make a basic pack!

[**Furry Therapy**](https://mega.nz/file/dakhzYqS#kHO61V6pEwaXqtTXE7SGVHVdHjUkxtXE6Vyg2uw-FPA)
**Version: 1.5** *[398MB]*
Meant to demo corruption and the corruption "fade" feature, this pack is for people who love hentai. That's it! There's no tricks or traps in here, nope, definitely not at all... The pack configuration will only change the corruption and corruption fade settings, so feel free to edit the rest of the payload to what you personally enjoy. And try not to stare for too long, it might have adverse effects~

## Frequently Asked Questions

>Q: Where do I download more packs?

A: Unfortunately, packs are kind of scattered about... Since there is no specific place to congregate Edgeware packs (to my knowledge), people usually end up posting them to their personal twitters or discord servers. Additionally, some people charge money for their own packs and/or bundle a complete copy of Edgeware with their pack, making it even harder to give a definite answer to this question.

There are a few places you can start, however. PetitTournesol's original github page has multiple packs, although they don't support new ++ features. ~~/r/edgingware on reddit is mostly focused to tech support, but there are multiple packs there, including a helpful reference pack.~~ [EDIT: subreddit died from automod because reddit sucks] ~~I believe hgoon.booru also has a thread for Edgeware packs on the forum, but since it's a bit of an obscure booru and requires an account to post, i'm sure many still fall through the cracks.~~ [EDIT: doesnt get updated much when I checked recently]

There is an [unofficial discord](https://discord.com/invite/9rxab3BSB8) that hosts a lot of packs, just know that I don't really visit it much since I tend to use discord sparingly. 

>Q: I found a bug!

A: Fantastic! (well, not really.) The best place to post something like this is the [issues page](https://github.com/araten10/EdgewarePlusPlus/issues), where it can be properly filed and looked at/addressed by us or other people/pull requests. If it is something that seems like it might be a personal issue or relating to your specific setup, feel free to drop me a line on twitter. Just know that I might not be able to personally fix the issue, especially if I can't replicate it on any of my machines!

To help make the issue easier for us to solve, [here](https://twitter.com/ara10ten/status/1789414192702730718) is a short (NSFW!) guide on how to properly report bugs!

>Q: Somebody sent me this pack and it's not working! I checked inside of it, and it has an entire copy of Edgeware with it? Can I put it into my pre-existing Edgeware installation?

You can go into the resource folder of the pack you got, extract everything inside of it, and zip it with a desired name. This way, you can import the pack normally. If you already have an install of Edgeware++, it is recommended you do this over using their installation unless it comes from a trusted source. While many people make packs like this to make using Edgeware simpler for people who have never heard of it before, there's also the possibility of the files being modified to be malicious.

If you know that the pack creator set specific config settings for their Edgeware installation pack, you can also create a "config.json" file inside your newly created pack zip, and copy all of the contents of their "config.cfg" into it. This will allow you to import their config settings in the *Pack Info* tab, near the bottom.

>Q: Do you plan on making a discord for Edgeware?

A: No, I don't have any plans for this. On top of not particularly liking discord both as a program and a company, I also sadly don't have the energy to manage and moderate a discord. Even if I made one just for development updates with limited public posting, it would essentially be what my twitter is but on a platform I use less often.

As mentioned a few questions above, there is an unofficial discord. Me and Marigold don't really have much to do with it, but a ton of people have joined it and there's loads of packs up there. Feel free to join but please don't message me about goings on in there- i'm not a mod or anything!

>Q: Can you give me more info on upcoming features?

A: I personally like to reveal things once they're at the point where i'm not going to turn back or change my mind on them, as I think sometimes revealing things too early kills motivation and adds a lot of stress. I also get easily distracted and absentminded (don't we all...) so I can't guarantee that anything I announce early will actually happen anytime soon. Because of this I don't like to give out information on upcoming features to people, but I do post general updates/ideas on my [bsky account](https://bsky.app/profile/araten.bsky.social) and [twitter account](https://twitter.com/ara10ten), which also serves as a point of contact/a place for me to ramble about horny things! You can also view planned features on the issues page!

>Q: Can we be friends/talk more/can I dom you?

A: I am a creature by night, and keep to the shadows. (this is an edgy way of saying i'm quiet and autistic, I generally have a low social battery)

But also feel free to follow me on twitter, interact with me there, and other such things! I don't bite!

>Q: Does Edgeware work on android/mac/ios?

A: I only have plans to develop Edgeware for windows, and LewdDevelopment is currently only developing Edgeware for Linux.

>Q: Are there other programs out there like Edgeware?

A: The main one that comes to mind is [goonto](https://github.com/dogkisser/goonto), which is similar to Edgeware but without the need for packs or a python installation (also works on macOS for those of you with the question above this one).

[Walltaker](https://walltaker.joi.how/) is also pretty popular, but is much more social and only focuses on changing your desktop wallpaper.

>Q: Why did you change the default loading splash and icon?

A: We wanted to play it safe and find a more generally SFW appropriate image for the splash screen to assist in distribution across multiple sites. While the new splash screen is still plenty horny (and also a caption by yours truly), it has less a focus on genitals and other such things that could potentially cause issues down the line. The icons were fine, but it felt fitting to match them to the new theme. I apologize in advance to PetitTournesol for semi-de-branding their program!

## Changelog

The changelog can be viewed [here](CHANGELOG.md).

## Content Removal Policy

If you are the owner of any art or assets used by this program or linked demo packs and are unhappy with their usage, feel free to contact us through twitter or discord and we will happily work things out (assuming we are still active/around/alive at the time of messaging). Please note however, that any pack *not* linked on this page is either by somebody else or for private use. We offer "pack creation tools" for users to make packs of their own liking, but we have no control over what is done with them or how they're distributed.
