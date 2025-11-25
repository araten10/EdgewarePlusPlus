# Edgeware++
![Edgeware++ running on Windows 11](screenshots/demo.png)
## What is Edgeware++?

Edgeware++ is a fetish-designed program (so 18+ only!!!) that essentially spawns popups over your screen in many different ways. These popups can include images, videos, audio, prompts, etc. It's also highly customizable, with the ability to download "packs" people have made and use them yourself. It can be ended at any time and also scheduled in ways to be used more passively.

Originally inspired by "Elsaware" (which, truthfully, I know nothing about), the original Edgeware's goal was to be a "fake virus" program that looked like your computer was being taken over by porn. Edgeware++ is an extension of this program, and has a ton of new features and bugfixes. I used to write down a list of them in this readme, but it was starting to get way too long!

**Edgeware++ is not a virus, nor does it install itself onto your computer**. All it installs onto your computer by default is python and a few extra libraries (along with a portable version of 7zip on Windows to extract the video player), which is needed for it to run. Edgeware **can** potentially modify files on your computer, including deleting or replacing things, but these are all *user set* settings that are not on by default.

## Usage Instructions

All stable builds can be found in the "Releases" tab on the right (or [here](https://github.com/araten10/EdgewarePlusPlus/releases)), along with a brief summary of patch notes. Alternatively, if more up to date but potentially unstable builds tickle your fancy, you can click the big ol' "code" button in the top right, then "download zip".

Save and extract it somewhere, then run `edgeware/EdgewareSetup.bat`. This will install python for you, alongside some necessary libraries. After that it will give you instructions for further use, and open up `edgeware/config.pyw`. **Check the top of the installer window to see if you have an older version of Python installed!** Edgeware previously used python 3.10, and if you're using that version, you'll have to uninstall it to get the newest version!

**If you're using Linux**, first you need to install Python 3.12, pip, and mpv yourself, if you don't already have them installed already. Your distribution should contain packages for them. For example, on Debian and its derivatives, you can install them by running `sudo apt install python3 python3-pip mpv gcc python3-dev libmpv-dev python3-tk`. Once installed, download and extract Edgeware as a ZIP or clone the repository, then run `setup.sh` in a terminal window in the `edgeware` directory. This will create a Python virtual environment for Edgeware, install the dependencies, and create scripts for running Edgeware. `config.sh` allows you to configure Edgeware and `edgeware.sh` will start Edgeware itself.

From there you'll need an actual pack, which can be downloaded online or made yourself. Unfortunately at the time of writing there's really no congregated directory of packs everyone's made, they're all scattered to the four winds... but for a start [the original Edgeware page](https://github.com/PetitTournesol/Edgeware) has a few sample packs, and there's a few more in the "Packs" section of the readme.

Any time Edgeware has a major update, it might be a good idea to run `EdgewareSetup.bat` again, as this is the file that downloads dependencies for the program.

**Any damage you do to your computer with Edgeware is your own responsibility! Please read the "About" tab in the config window and make backups if you're planning on using the advanced, dangerous settings!**

We have also added a Pack Editor included with each copy of Edgeware++. It's a bit different if you're familiar with the old one- it runs in command line and has different features.

## Packs

For some of these packs, we will include a pack config file so you're able to easily test relevant settings. To apply these settings, you can go into the "File" tab once you've imported the pack, and press the "Load Pack Configuration" button. Once they've been loaded, you're free to take a look around and change anything you see fit, as the packs usually will only change a few settings. Make sure you save before you exit!

Reminder: Check out the "Pack Info" tab for more information on these packs once you download them~

### Basic Packs

These packs are the basic bread and butter of Edgeware++! No need to run them any special way, just load in and enjoy!

[**Edgeware++ Test Pack**](https://mega.nz/file/VbsEmbLD#gCLx6Ftv161oT7u3yiU8altS07QSElTz-Xo9kRmcugM)
**Version: 2** *[17MB]* *[No pack configuration!]*
The original test pack for Edgeware++! It's fairly old, and i'm not sure how much i'll be updating it in the future. However, it's completely SFW, has examples for most features up to version ~13, and is extremely small in the filesize department. This is a good place to start if you just want to test running Edgeware, or learn how to make a basic pack!

[**DemonDemo++**](https://mega.nz/file/5OcXzRzZ#WUPW1PuGEKO1bM3VJKMT6rNz6c4bxpgjHHAN9YQjr-Q)
**Version: 1** *[103MB]* *[No pack configuration!]*
Want to test out Edgeware++ with something a little more suitable for that *addict* brain of yours? Here's a small-sized pack perfect for testing the program's basic features! Comes with captions, a custom splash screen/wallpaper, some basic moods, and plenty of heretical demonic women~ This pack was also made with the new `index.json` method of pack creation, so its an example of how the new backend works, as well! Enjoy submitting to hedonism for us, we'll make sure to drag you aaaaalll the way down <3

### Corruption/Scripting Packs

These packs rely either on Corruption or Scripting to function as intended, and are designed as "repeatable experiences" that do things over time. Make sure to load the pack configuration if they have one, without it they'll likely do weird things or act incorrectly!

[**Furry Therapy**](https://mega.nz/file/dakhzYqS#kHO61V6pEwaXqtTXE7SGVHVdHjUkxtXE6Vyg2uw-FPA)
**Version: 1.5** *[398MB]* *[Has pack configuration!]*
Meant to demo corruption and the corruption "fade" feature, this pack is for people who love hentai. That's it! There's no tricks or traps in here, nope, definitely not at all... The pack configuration will only change the corruption and corruption fade settings, so feel free to edit the rest of the payload to what you personally enjoy. And try not to stare for too long, it might have adverse effects~

[**Addict Acceptance Program**](https://mega.nz/file/dSd3HJpA#6hNJyg9IgiBqGAqIsnvKcGV1Bq7oeK1f5I9g6nueh6I)
**Version: 1** *[1.71GB]* *[Has pack configuration!]*
An absolutely massive and ambitious JOI pack fully voiced by [Mistress Yumiko!](https://hypnotube.com/user/mistressyumiko-159116/) Designed to show off the new pack scripting features added in version 19, this pack will tease and degrade you while going through all of the current major features of Edgeware++! It took a long time for us to make this, but it was totally worth it! Best to wear headphones and turn the volume way up, and let those commands wiggle their way into your ears~ *Note: the dialogue in this pack uses male-leaning pronouns and commands, and also features several "beta-safe" degrading fetishes. These can be disabled via the "moods" tab, but it will not change the voice acting of the pack. Also this pack* **absolutely requires version 19 of Edgeware++ to run properly!**

Yumiko did us a huge solid in helping us out with this pack, so if you like her work here, consider supporting her on her [patreon](https://www.patreon.com/cw/MistressYumiko/)!

## Frequently Asked Questions

>Q: Where do I download more packs?

A: Unfortunately, packs are kind of scattered about... Since there is no specific place to congregate Edgeware packs (to my knowledge), people usually end up posting them to their personal twitters or discord servers. Additionally, some people charge money for their own packs and/or bundle a complete copy of Edgeware with their pack, making it even harder to give a definite answer to this question.

There are a few places you can start, however. PetitTournesol's original github page has multiple packs, although they don't support new ++ features. /r/edgingware on reddit is mostly focused to tech support, but there are multiple packs there. There is also an [unofficial discord](https://discord.com/invite/9rxab3BSB8) that hosts a lot of packs, just know that I don't really visit it much since I tend to use discord sparingly.

>Q: I found a bug!

A: Fantastic! (well, not really.) The best place to post something like this is the [issues page](https://github.com/araten10/EdgewarePlusPlus/issues), where it can be properly filed and looked at/addressed by us or other people/pull requests. If it is something that seems like it might be a personal issue or relating to your specific setup, feel free to drop me a line on twitter. Just know that I might not be able to personally fix the issue, especially if I can't replicate it on any of my machines!

To help make the issue easier for us to solve, [here](https://twitter.com/ara10ten/status/1789414192702730718) is a short (NSFW!) guide on how to properly report bugs!

>Q: I'm having a problem running Edgeware, should I run it as administrator?

A: No! With the only possible exception of the Python installer, no part of Edgeware should require elevated privileges. This includes the setup script, the config, Edgeware itself, and the Pack Tool. Running any part of Edgeware as administrator is unlikely to solve your problem and may only create more.

>Q: Somebody sent me this pack and it's not working! I checked inside of it, and it has an entire copy of Edgeware with it? Can I put it into my pre-existing Edgeware installation?

A: You can go into the resource folder of the pack you got, extract everything inside of it, and zip it with a desired name. This way, you can import the pack normally. If you already have an install of Edgeware++, it is recommended you do this over using their installation unless it comes from a trusted source. While many people make packs like this to make using Edgeware simpler for people who have never heard of it before, there's also the possibility of the files being modified to be malicious.

If you know that the pack creator set specific config settings for their Edgeware installation pack, you can also create a "config.json" file inside your newly created pack zip, and copy all of the contents of their "config.cfg" into it. This will allow you to import their config settings in the *Pack Info* tab, near the bottom.

>Q: Can you give me more info on upcoming features?

A: I personally like to reveal things once they're at the point where i'm not going to turn back or change my mind on them, as I think sometimes revealing things too early kills motivation and adds a lot of stress. I also get easily distracted and absentminded (don't we all...) so I can't guarantee that anything I announce early will actually happen anytime soon. Because of this I don't like to give out information on upcoming features to people, but I do post general updates/ideas on my [bsky account](https://bsky.app/profile/araten.bsky.social) and [twitter account](https://twitter.com/ara10ten), which also serves as a point of contact/a place for me to ramble about horny things! You can also view planned features on the issues page!

>Q: Can we be friends/talk more/can I dom you?

A: I am a creature by night, and keep to the shadows. (this is an edgy way of saying i'm quiet and autistic, I generally have a low social battery)

But also feel free to follow me on twitter, interact with me there, and other such things! I don't bite!

>Q: Does Edgeware work on android/mac/ios?

A: I only have plans to develop Edgeware for windows, and Marigold is currently only developing Edgeware for Linux.

>Q: Are there other programs out there like Edgeware?

A: The main one that comes to mind is [goonto](https://github.com/dogkisser/goonto), which is similar to Edgeware but without the need for packs or a python installation (also works on macOS for those of you with the question above this one).

[Walltaker](https://walltaker.joi.how/) is also pretty popular, but is much more social and only focuses on changing your desktop wallpaper.

I've seen a few paid programs out there, but have no idea how they work or if they work well. I assume they're closed source, and i'm not too interested in experimenting with gooner programs that can change my PC unless I can see how they work.

>Q: Why did you change the default loading splash and icon?

A: We wanted to play it safe and find a more generally SFW appropriate image for the splash screen to assist in distribution across multiple sites. While the new splash screen is still plenty horny (and also a caption by yours truly), it has less a focus on genitals and other such things that could potentially cause issues down the line. The icons were fine, but it felt fitting to match them to the new theme. I apologize in advance to PetitTournesol for semi-de-branding their program!


## Content Removal Policy

If you are the owner of any art or assets used by this program or linked demo packs and are unhappy with their usage, feel free to contact us through twitter or discord and we will happily work things out (assuming we are still active/around/alive at the time of messaging). Please note however, that any pack *not* linked on this page is either by somebody else or for private use. We offer "pack creation tools" for users to make packs of their own liking, but we have no control over what is done with them or how they're distributed.

## License

As of April 28 2025 all future versions of Edgeware++ are licensed under the GNU General Public License version 3 or any later version. Contributions prior to the specified date are licensed under the MIT License.
