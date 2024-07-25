## EdgeWare++ Patch Notes
**If you see that there's a new update and are somebody (like me) who is lazy and doesn't like installing every single update if unnecessary, here is how I do versioning:**

•+1.0 to version number: multiple new features, or a single large feature

•+0.5-0.25 to version number: new feature, but a smaller one or something not as essential, or lots of bugfixes

•+0.2-0.1 to version number: very small update, usually just a bugfix, accessibility options, UI tweaks

**Since last version...**

•*Mitosis mode tagged as a dangerous setting, danger level "medium"*

•*Cleaned up log files so there's less benign errors being thrown for no reason*

•*Changed sublabel mood from "subliminal" to "subliminals", to keep with consistency on config window and everything else i've mentioned about them*
>Apologies for not catching this one sooner- if you already made a pack with this and knew about the issue so you changed it, you might need to change it back!

•*Removed multiple unused variables from config*
>This might require you to remake your config file!

**Version 11**

A lot has changed! So much so that I actually am having the unique problem of having to *look up* what was fixed since the last version. This is because **LewdDevelopment** has been helping catch me up to speed on Github and we've been rolling out smaller updates, using branches, etc.

•*Corruption has been added in a beta-like state*

•*The test pack has been updated to be able to test corruption*

•*Restored some basic functionality to the booru downloader (thanks @TallLeaf!)*

•*Moved a bunch of backend files to a subprocesses subfolder, to reduce confusion for new users*

•*Changed the default config file into a JSON file*
>This will break the "Edgeware Update Checker" in older versions, but luckily it will tell them to update regardless

•*Simplified a bunch of backend and condensed backend PATHs*

•*Cleaned up the github pages and moved the changelog to it's own .md file*

•*Added a setting to subliminals that allows you to change the transparency*

•*Fixed bugs that might have affected corruption*
>If you had issues with launching popups before, this probably fixed it!

**Version 10.2**

Continued work on corruption among other things. There might be big changes happening to this github page, as I am now working with a friend (@ecchigooner) and they are helping me actually understand github instead of pretending to understand github. This actually might be one of the last times Edgeware updates like this, as i'm hoping to get a grasp on releases and making things actually semi-official instead of whatever i'm doing right now...  

•*Example image added to readme, along with some readme changes that will continue with future patches*

•*Commented out the display tree on the corruption page for now, something like it will return but I want to focus on finishing corruption before having to debug it!*

•*Backend work on corruption*
>Startup now checks for a corruption data file

•*Implemented "Dev Mode" in the corruption tab, which overlays information very unsexily on popups*
>This currently includes filename and current corruption level, but might be expanded in the future. Let me know if there are any developer statistics you want to see!

•*Edgeware Setup now downloads things from the requirements.txt file on first startup*
>If you've already previously run edgeware and had it work fine, no need to do this

•*Removed scripthandler.py and some unfinished "script mode" code*
>We're trying to clean up edgeware a bit to make it easier to understand, and in doing so we're realizing that this script mode ended up going completely unfinished and was likely the last thing petit worked on before disappearing.

**Version 10b**

Quick and dirty bugfixes to a few problems that have popped up since version 10's release. I might have to go do *shudder* actual work for a week or so, so I wanted to get out critical bugfixes before I go anywhere.

•*Fixed custom startup flairs not loading*

•*Fixed start.pyw crashing on windows if create desktop icons is enabled*

KNOWN ISSUES:

•*I have narrowed down the old pack compatibility issues to the multi-click popup update causing very basic captions.json setups causing issues. I will look into fixing this as much as I can, at the very worst I can hack some sort of compatibility check in which i'm sure will make future contributors to these forks hate me*

•*All other known issues from 10a still persist, as they were not critical to most edgeware operation*


**Version 10a**

Another month, another long story~! So I got roughly halfway through working on corruption, and was going to ship a small version, likely 9.5 or 9.6, then was sent a DM with some interesting new features. I decided heck, since they're already programmed and were things I wanted to do anyways, i'll add them in. Then when I was about done with them, I got sent another DM with fatal bugs that definitely should be fixed sooner than later. While looking into potential causes and ruminating it on twitter, I got sent another DM from somebody who submitted a pull request for Linux compatibility, saying they already potentially fixed the bug since they noticed some things that were wrong. So then I went and merged the linux pull request and did some bugfixes while talking with the person who submitted it to iron some things out. Eventually I just said "screw it", and decided this was large enough to be a full new version. Theoretically I could name it 9.9 to keep my promise of corruption being finished by version 10, however I think i'd rather stick to more consistent versioning rules (as consistent as I get with them, at least) than try and make a loophole for my own problems.

Anyways, this is probably one of the largest updates EdgeWare++ has ever had. Because of that i'm cautiously appending an "alpha" label onto it, in case the weight of it causes more bugs than usual. As always, if this catastrophically doesn't work, I will try my best to fix it ASAP!

•*Actually fixed the bug "hotfixed" with 9.3a properly this time, making the pack config preset button deactivate when no config.json is loaded*

•*Removed "prefix_settings" from the captions mood treeview as it's something that slipped past me and I guarantee disabling it would break everything*

•*Stopped Timer Mode automatically adding a startup script, as I feel like it doing so was a hidden quirk that isn't totally obvious to new users. Instead, enabling Timer Mode now automatically enables Run on Startup, which is visible in the config window and can be turned off if the user desires.*
>In practice, this should work exactly the same as it used to, with the main difference being that users can now tell Timer Mode also enables Run on Startup. They also can uncheck Run on Startup if they just want Timer Mode without it enabling every time they restart their PC.

•*Turned off "Show on Discord" for default config setting*
>Listen, i'm all for retaining as much of the original edgeware as possible but after having this almost cause an accident on my work account and also hearing somebody not know it was a feature after running edgeware for ten minutes i'm inclined to turn it off for your first launch

•*A ton more frontend work on corruption*
>Most, if not all of the corruption settings I plan to ship version 11 (or whatever it will end up being at this point) with are now in view on the corruption tab, the backend is still not there yet but that will be done over the following patches

•*Fixed some minor issues with prefix_settings in the config window, for the 2 packs that have managed to implement multi-click popups without the pack editor update*

•*New popup type: Subliminal Messages!, originally by /u/basicmo!*
>These can be found in a new sub-section in the annoyance window, and use the captions.json file to flash short messages up at you. Their appearance is based on the theme you've chosen, and can use a new mood called "subliminal" to specifically label shorter captions (like "OBEY", or "GOON") that won't show up on popups.

•*New popup type: Moving Popups!, originally by /u/basicmo!*
>This will make popups have a chance to start bouncing around all over your screen, like an old DVD player screensaver. There are multiple slider settings for this in "annoyance". To make it not impossible to close these popups, anything that turns into a moving popup enables the "labeless" property.

•*Basic linux compatibility may or may not work now!*
>Please read the above "Usage Instructions" section for more info on this! This is a huge reason why this update is labelled as an "alpha", so please note it might not fully work! Bug reports are appreciated!

•*Fixed a huge issue with audio error checking that could cause the whole program to not load, and captions.json causing crashes when undefined*

KNOWN ISSUES:

•*I have noticed that Timer Mode in itself is very buggy- something that I haven't really touched much before. For me on Windows 11, it appears that it is hard to consistently panic, tray panic doesn't seem to work at all, sometimes the command window pops up and sometimes it doesn't. I haven't really touched it and theoretically nothing I added should affect how it functions, so I am not sure if it was this buggy with original edgeware or if it is indeed my fault. Alternatively, it could be compatibility problems with my setup. I will try to bugfix it to the best of my ability but for the time being know that I'm aware of it's odd behaviour.*

•*In some cases, packs that worked with old EdgeWare no longer work in ++. I have only seen this happen with two packs, and have yet to completely figure out why, but it might have something to do with how their captions are set up. I'm going to continue looking into this over time and seeing if I can get full 100% compatibility with old packs, even if they're so old or basic that they are structured very differently to everything else.*

•*If you don't launch the config window at least once, the mood feature absolutely explodes since it hasn't generated moods. I understand nobody's probably using moods yet, but for the time being... if you're moving all your files in the resource folder to a new install or update, make sure to launch the config window once! This should be one of the simpler things to fix, and will be pushed sometime soon*

•*The default theme for subliminal popups is black text, which means that on a lot of "ahegao wallpapers" that are black and white it might have troubles with visibility. Currently brainstorming ways to fix this, between either an outline or just allowing users to set their own colour*

**Version 9.3**

Remember about how I was banned from reddit because automoderation deleted my account thinking I was a spambot? Now twitter banned me because it said I was "evading suspension" (despite not having any other twitter accounts)! Turns out this is happening to a ton of people, it seems to be some strange bug that is just mass banning people. In theory this should be fine and I should get my account back, but it's twitter, and considering how dismal the automated support I got in trying to appeal this has been so far, I don't have much hope. I kind of feel like the outcome will be acknowledging the bug but not reinstating my account.

I'm kind of frustrated as this is the second account i've had suspended in a week by automoderation not working properly, so I think i'm going to just take a break for a short bit and cool off. Luckily, this update (should) be stable enough to launch as the last major feature I worked on I managed to finish before this happened. There will be a few new things that are unimplemented, but they're all related to the corruption tab so not a huge deal. Especially for this update since i'm pushing it out, if you see any fatal bugs let me know so I can fix them!

•*Moved the corruption path to the corruption tab*

•*Also axed the corruption path "fancy text", since it didn't play well with most themes, and was overly code heavy for what it was*

•*Added a "Pack Config Preset" setting in the "Pack Info" tab, which allows for pack creators to make settings presets for their packs. These are not automatically saved, and the user can view the changes before deciding to save themselves or simply exit the program.*
>To make one of these for your pack, create a "config.json" file in your pack resource zip. This follows the exact same formatting as a regular config file, but doesn't need all of the arguments to run properly. For example, if you just wanted to change popup delay to 5 seconds, you could just create a config.json file with the contents {"delay": 5000}. Alternatively, you could also just save your config.cfg, and copy it over to this json file, whatever is easier.

*Added a few more backend things to the corruption tab, progressing it's status from "unimplemented" to "still unimplemented, but closer to completion".*

**Version 9**

Probably not what you were expecting, or when you were expecting it! In short, I fell victim to the "post-holiday haze" and proceeded to not really work on anything for half a month after new years. Then I finally decided to light a fire under my ass after hearing multiple reports for pretty serious bugs that I wasn't even aware existed... but after being absent for a month, my brainworms also told me that I probably should release an actual feature alongside it. So I decided to work on something "less convoluted" than corruption, and implemented themes instead. (turns out this was harder to implement than I thought)

Work on corruption will proceed apace next update (unless I get distracted again)

•*Added checking for mood toggle on web treeview load, so config doesn't throw errors even if moods are toggled off*

•*Made the in-config error log more descriptive and less scary sounding*

•*Fixed a bug that made animated gifs no longer work on the newest version- apologies for the delay on getting to this!*

•*Fixed a bug with importing ttkwidgets that could cause errors the first time you launch the program*

•*Changed the messagebox popup for version mismatch (which I forgot existed until now) to check for ++ version instead of base version*

•*Added support for themes, including 6 themes to choose from. Original and Dark for something more standard, and four alternate "fun" themes to pick from!*
>Some things might look different even if you stay on original, I had to change a few values to make themes compatible- please let me know if this breaks anything on your end!

•*Added a link in this readme to my twitter. Follow me there for development updates!*

KNOWN ISSUES:

•*Switching between themes sometimes breaks the label in the preview window, making it disappear.*
>I was worried this would also happen when you actually apply the theme, but I have not seen it happen yet on my end. Not sure what the bug is or how to fix it, so will keep it as it is unless I hear it's happening to things outside of the theme preview.

•*Some coloured text displays mono-coloured when using a non default theme*
>It's not a huge deal and would be a pain to go through and implement this right now, but just know that some things previously highlighted red and green will now be whatever text colour the theme switches to instead.

**Version 8.2**

Likely the last time I work on EdgeWare before the new year if I had to guess- you know, holiday stuff! Version 8 was more stable than I expected, having only one person report a bug that caused nothing to work. I fixed that, and also got around to adding another pull request in from TheoWinters that fixes some minor errors and adds new functionality to captions.

•*Fixed a bug that made it so not having a "media.json" file threw errors unless you turned moods off.*

•*Forgot to take out an error testing messagebox for people who used the "on popup close open weblink" option, it's gone now*

•*Added some more error checking around importing VLC, in an attempt to make it less catastrophic if something goes wrong*

•*Fixed VLC mode not letting you close popups if you were also using buttonless mode*

•*Expanded captions.json to include several new features for pack creators. More information on this can be found [here](https://github.com/araten10/EdgewarePlusPlus/pull/3). Updated captions.json example in example assets as well.*
>Note to self/other people who are trying to get these to work: if you leave the comments in, when you pu

•*Likewise, added a feature in config that allows for multi-click popups*

•*Testing out finally using a .gitignore file, so now I can actually work in the folder i'm using for github...*
>I genuinely had zero experience with github before doing this project, I made this account purely for EdgeWare, so it was to be expected I also don't really understand how to have a sane and reasonable workflow with it. This won't affect anything on the frontend unless something slips through and I accidentally end up uploading porn

**Version 8b**

Uwaaaaaaaaa! Mood blocking is here finally~!

I am putting "b" for "beta" at the end of this version, because admittedly I am rushing this update out. I changed a lot and added a lot, but won't be able to test this as much as i'd like- I am leaving the house for holidays, and I know coming back I will not be in the same mindset. So I wanted to get this update out before I go, even if it's potentially buggy with some issues. Do not hesitate to download an older version or keep your previous version of edgeware as a backup, just in case.

I originally planned for this to be a small update, but things kept getting added and I got closer and closer to implementing moods. While I am away I will not be able to work on EdgeWare, but any bug reports or issues I hear about I will do my best to fix ASAP as soon as I get back. I want to do a cleanup update next to try and fix some things.

•*Custom loading splashes now support .gif (won't animate, sorry), .bmp, and .jpg/jpeg*
>I tried to make animated gifs work, but couldn't figure out how to bugfix infinite iteration errors- I commented out the code but kept it in, in case I come back to fix it later (or somebody else does).

•*Added web moods. No pack will currently support it, but the functionality is there for future packs. It is* **HIGHLY** *recommended you delete all previous mood files to let the newer versions populate with web features.*
>Admittedly only reason I didn't add it before now is because I never use web links and totally forgot...

•*Added "id" to info.json- apologies to the two people who have already made edgeware++ packs. Use it for hooking into moods similar to how the name of the pack used to do. No spaces or special characters, or else it won't work!*
>Decided to nip this in the bud and add it in- if people put spaces in their pack name (incredibly common) or other non-accepted characters, it would mess up a lot of things down the line. Instead of forcing people to do certain naming conventions, the better option would be to split the mood ID and the name into two separate values.

•*Added info.json and media.json template files to "example assets", if you want to make packs with them before the pack editor update. Also updated older example files.*
>corruption.json will come in future updates when I finish implementing it fully

•*Prompts, captions, and media (if set up) can now be blocked by mood.*
>The only thing that can't currently be blocked by mood is weblinks, but that's fine because it's a new feature that won't be supported by any pack. I wanted to get it fixed before this update came out, but ran out of time unfortunately. Will be patched in to a later update.

•*Added "Single Mode" in the annoyance tab, a toggleable option to only allow one popup to spawn per popup roll. Removed single mode being auto-enabled during hibernate mode.*
>See version 7.5 patch notes for more information on what this entails

•*Made the config window much taller, and changed some things to have the "Save and Exit"/"Resources" buttons more reliably show up.*
>I can't imagine using all this space, but I wanted to increase it as things were getting pretty claustrophobic and I didn't want to have to compromise features to fit it all in there.
>I know that some users might be running EdgeWare on lower res displays and don't want the config screen so big- you can still freely resize the config window to fit it back to it's older resolution. For those who are running EdgeWare on your 320x240 arcade cabinet displays (god bless you), I have purposefully made these the first settings on the "File" tab so you can access them there. If I get around to programming themes into EdgeWare I will consider an ultra-compact theme for this...!

•*Renamed the "Advanced/Troubleshooting" tab to just "Troubleshooting", mainly to save space on the tab bar*
>I plan to at least add one more tab (expanding corruption to it's own menu), so I want to keep people with smaller monitors in mind.

•*Added the Corruption tab, for the next major update, coming soon...*

•*Fixed video volume not working on VLC mode*

•*Fixed VLC videos not looping*

•*Edited the web.json file in "example assets" to correlate with this change.*

•*Some backend changes and cleaning, shouldn't affect anything for the end user (hopefully)*

•*Fixed a bug that made it so EdgeWare++ packs wouldn't have their moods properly set*

•*A few more tooltips here and there, you know how it is*

•*Added version 1.0 of Edgeware++ Test Pack.*

KNOWN ISSUES:

•*VLC can potentially not work if the PATH is not set to VLC. Currently not sure how to fix this issue, but will look into it. You can manually set the PATH yourself to the vlc directory.*

**Version 7.55**

•*Bugfix on VLC Mode that wouldn't install VLC unless you had it enabled, causing errors in popups*

**Version 7.5**

Was given a potential solution for fixing video issues that people have been having since the original EdgeWare, and decided to take it. Releasing a short-but-hopefully-sweet update to patch it.

•*Added a new mode for video playback: using VLC to play videos. Toggle it on/off in the troubleshooting tab.*
>You must have VLC installed for this. This should help people who were having audio issues with videos and it's also a lot faster to load.

•*Trialing a new "more consistent popup experience" by making it so popups can only "roll" once per spawn. This mostly affects having videos or audio at very high percentage values- before the change they would also be accompanied by a regular popup. Currently only enabled for hibernate mode*
>I kind of like the randomized-ish experience of having potentially more popups than expected, but also for things like hibernate mode you probably want something more consistent. I'll keep it on hibernate only for now while I consider what I want to do with this.

•*Worth bringing up even though it was added slightly before: merged a pull request from a fine contributor that allows for non-animated gifs to be used properly!*

**Version 7.2**

Once again dealing with "way too many projects at once and games to play", pardon the delay...

Small one to get back into the swing of things. Still planning the next update to be finishing mood implementation. I was seriously tempted to work on it and try to cram a bunch in a larger update, but I regained control of myself and pushed out a smaller update now rather than delaying the whole thing to fit more in.

•*Fixed a bug that caused the startup splash to display every time the "Pump-Scare" hibernate mode activated*
>Another bug I didn't discover until now. Was a really easy fix, sorry if you've been bothered by it for a while!

•*Fixed a bug that might have blocked pump-scare from working for packs without audio*

•*Added "Pump-Scare" to Chaos Mode, finally*
>I kept putting this off because I wanted to figure out an elegant solution to add it without embarrassingly bad code, then I remembered that my whole ethos with this project is "just don't worry too hard, as long as it works". I think I could remove a few .dat files i've created over time by learning and properly implementing system args on file execution, but maybe another time.

•*Added a feature to the troubleshooting tab allowing Pump-Scare offset*
>I have debated for a while what I should do regarding this. I have known since the beginning that pump-scare's audio won't play when it should for any reasonably sized sound. I tested with various file sizes, and anything over 5MB will start to add delay (at least on my computer). It's obviously not reasonable for pack creators to compress their sounds this much, and I think anything that small would be so short it would only work for pump-scare and nothing else.

>To put it shortly, the audio playing module "playaudio" is very feature bare. It doesn't support pretty much anything other than just playing an audio file, and that includes multithreading. I did a workaround with multiprocessing but at the end of the day there's no way to wait for the audio to load before playing it. The problem is that being barebones is kind of the point of the module- sure, I could import pyglet or pygame and have full audio controls, but then i'd feel bad getting users to download an entire game development module just for reasonable audio playback. This is a temporary measure to keep things "as they were" for now, but maybe someday i'll come back and update it to a new system.

**Version 7**

Gee howdy, it's been a long time, huh! Life stuff happened, then I got sucked into another project, then halloween happened... busy month.

I really wanted to fit everything left I had planned before starting work on the pack editor in one huge mega-update, but unfortunately I found other bugs in the program, heard some more feedback, also was busy with other things... I felt like it was better to release it into smaller chunks. In 7.0 there are a couple bugfixes, a couple new features, and a couple features that are added to the config window but currently aren't implemented. Hopefully the last thing is more an exciting preview of things to come and less something that confuses everyone who uses this version~

•*Fixed a minor bug in the troubleshooting tab that led to the wrong tooltip displaying*

•*Fixed an actually nasty bug that disabled internet connection to github every time you didn't have a config file loaded*

•*Made the disabled features a slightly lighter shade of grey, for both readability and also just easier on the eyes*

•*Un-expanded certain sections in the config window which might have caused the "Save & Exit" button to be wiped from existence for some users. If this problem persists, I also added these buttons to a more safe space in the...*

•*...Brand new "File" tab, which is the place for all your file management needs.*
>Options for saving & loading, opening certain folders, and deleting logs (because I hated doing it myself). I also moved the "Config Presets" section here to make space for new features in the general tab. (I still want to do themes someday!!)

•*Pack Info now contains a "moods" section, where you can view/toggle moods, and look at the pack's Corruption Path.*
>HUGE asterisk: toggling moods on and off currently does nothing. That being said, you can still see the list of moods and number of items relating to each mood. You can also toggle these on and off pre-emptively (which will save properly) for when I release the next update which will (hopefully) add proper mood toggling. What's Corruption Path? Well...

•*Added various settings and framework for a new "Corruption" mechanic, but... it's currently not implemented!*
>I wish I could say "Happy Halloween" and release a spooky update involving a feature designed to slowly rot your brain with more degenerate fetishes, but I guess I missed the boat on that one. Feel free to toggle or mess around with any of the settings, they don't do anything at all currently.

KNOWN ISSUES:

The original demo packs for regular EdgeWare sometimes use the "default" mood as a completely separate mood, while other packs use it as the ONLY mood... For now I have made it so you cannot disable "default" so mood editing plays nice, but in the future I might change it to be toggled.

**Version 6.0001**

•*Updated the readme (the thing you're reading right now!) to actually explain what edgeware is and how to use it. Removed the old edgeware patchnotes because they were super long and i'm not sure how helpful they were when you can just go to the original page*

I'm currently working on another huge feature, and i'm unsure if i'll release it in small steps or all at once. Keep an eye out!

**Version 6**

**THE FUTURE OF EDGEWARE++**

You normally see this header when something is being deprecated, sunset, or no longer being worked on. Luckily I want to say right out the gate, that this is not the case. I do want to approach this subject though, as the next few updates might be a bit different than those previous.

I am nearing the end of my planned features for EdgeWare++, most of which are things that I went "man, it should have this as an option" when I first used the original program. Pretty much everything left is getting exponentially larger to tackle, which is partially why i've procrastinated on adding them. There's a bigger issue in the back of my mind though, and that's the pack editor. The more features I add to EdgeWare++ that let people do fun stuff with packs, the more the pack creator needs to know how to manually add in, since the pack editor is still configured to the base version and has no new features. Additionally, the pack editor is feature-light in general.

Because of this, I am planning to have version 7 or 8 be the *last version of EdgeWare++ for a while*. This is only because I want to focus instead on the pack editor, and I think it will only take 1-2 more versions to add the major features to packs that I want to add. After that, I might come back to EdgeWare++, I might take a break, I might be satisfied enough and move on, i'm unsure (mostly depends on how hellish it is switching to a new project). The last major features I want to add before then is mood blocking and "mood corruption", both of which I will go into more detail as they come out.

Of course, I could always get distracted and work on other stuff here first. This is not set in stone as I know full well that I get easily satisfied adding lots of small, easy features instead of huge ones that can take weeks to work on. Just wanted to lay out the groundwork and let people know what i'm thinking about moving forward.

•*Added troubleshooting option to disable connections to github for users with slow internet*

•*Added errors section to troubleshooting with some non-fatal errors able to print user-facing logs there (there are still more detailed logs in the subfolder, though!)*

•*Fixed some error checking \*ahem\* not existing, config should no longer crash if (most) non-essential files have errors in them*

•*Added official support for info.json in pack files.*
``{"name":"", "creator":"", "version":"", "description":""}``
>Anything left blank will be set to a default value. File does not have to be included at all, and all it does is give the user more information on your pack in the pack info tab. Max suggested characters for name/creator/version is 20, and any description longer than 400 characters will be cut off with [...]. I plan to put all of this in the pack editor soon with these values included.

•*Changed preset description to be handled by TextWrapper instead of the tkinter wraplength modifier*
>In short, things might look different than before but will wrap lines a lot cleaner

•*Added short hibernate mode timers to dangerous settings list*

•*Added feature in troubleshooting to skip directly to hibernate starting*

•*HIBERNATE OVERHAUL: added "hibernate types", which change how hibernate works. Also added a feature to change wallpaper back to your panic wallpaper once hibernate is done.*
>full documentation on the different hibernate types and how each one works is available in the "about" tab.

KNOWN ISSUES:

-Pump-Scare is not eligible for chaos, mostly because it taps into the popup itself directly and I want to get this update out sooner than later

-Hibernate modes might randomly drop popups, thus having less than expected range. This (shouldn't) affect the wallpaper fix setting, and upon testing an old version of edgeware this also happened with the original mode, so it might not be something worth fixing

**Version 5.2**

Small version while I mentally prepare for what i'm planning to do next...

•*Added feature to change icon file per pack. Uses "icon.ico" in the resources folder if there's one there, and default if not*

•*More tooltips!!!*

•*Added all of the currently added features to the top of the readme because honestly who wants to scroll down this far to get to the good stuff (is this even worth putting in the patch notes?)*

**Version 5.1**

It's the cleanup update!!!!!!! I recommend you do a fresh install, or at least delete the old clutter.

•*Moved max_subliminals and max_videos to /data/, because frankly I dont know what I was doing putting them in the root and I hated looking at them. The old ones can be safely deleted*

•*Deleted config-old, which was an ancient version of EdgeWare that didn't even run anymore*

•*Made the decision to turn on lanczos in the default config settings, because most people i've run into need to use it*

**Version 5**

Probably the **biggest** version yet if we're going by code added! But there's only two things changed:

•*Moved the import and export resources buttons to the bottom of the config window, and made them visible wherever you go*
>The people I have helped figure out EdgeWare with no prior experience had a near 100% confusion rate on what to do with packs, so I wanted to make it at least a little more clear. Might add a tooltip for them later.

•*Added a new tab: Pack Info, which allows you to see a ton of stats relating to the currently loaded pack. Current sections are Status, About, and Stats*
>This was a lot to add, so if there's any bugs with EW++ so far it'll all be here. Hopefully manages to be stable enough. Currently adding an about.json to your pack does nothing, but I wanted to add the framework for it since it's probably going to be one of my next added features.

**Version 4.8**

Wow, lots of small updates in a row!

•*Edited EdgewareSetup.bat to have easier to read text and also be more clear on next steps. It also now goes to config.pyw on completion rather than starting it immediately*
>Was helping somebody set up Edgeware and realized how confusing the initial startup is for some new users. Tried my best to demystify some of how to use it if you're not totally familiar with python programs. Changing it from start to config was so it didn't start barraging you with popups containing black circles before you even know what's going on

•*Further clarified a few things in the config window, added a tooltip or two, and added "troubleshooting" to the advanced tab name, since it contains a potentially important bugfix*

**Version 4.75**

•*Added troubleshooting tab and a setting to change from the antialiasing algorithm to lanczos*
>Some kind users on discord pointed out that popups weren't working, turns out somebody figured out that changing the resize algorithm from antialiasing to lanczos worked for them. This is code I didn't change for EdgeWare++, so maybe this has been a problem all the way from the original EdgeWare. Antialias has always worked for me, so to keep things as compatible as possible, i've added a toggle rather than just changing it over to the new algorithm. Hopefully this fixes some issues for people!

•*Added "buttonless" mode that allows you to click anywhere on the popup to close it*
>A feature request from discord, which somebody else already implemented for people who wanted it! Decided to add it as a toggle here. Thanks!

**Version 4.5**

•*Added version number, and EdgeWare Config checks to see if the GitHub is more up-to-date than your current version*
>I'm not planning on messing with any of the failsafes and auto-updates for the moment, and because of that I took out the not-implemented "download ZIP" button from the original release. This is so far the only thing i've removed from the original EdgeWare, but it also didn't do anything.

•*Added way more tooltips to things*

•*Fixed some dangerous option tooltip errors and added "Replace Images" as a dangerous option*
>I never used Replace Images and it turns out that it does what I thought "Fill Drive" did, so i'm glad I caught it while making tooltips!

•*Very minor changes on some button/slider labels for improved clarity*

**Version 4**

•*Finished max subliminals*

•*Added feature to receive warnings on having "dangerous" options enabled, will confirm with you before saving*
>The list of dangerous options are as follows: Run on Startup, Fill Drive, Timer Mode, Show on Discord, Disable Panic Hotkey, Run on Save & Quit. They are categorized into varying levels of severity.

•*Added tooltips on hover in the config window*
>Currently only added to the Warning on "Dangerous" Setting, mostly added to clarify which settings are considered "dangerous", but I might add it to more settings in the future so you don't have to cross reference the "about" page.

•*Added these patch notes in the "EdgeWare++" about page, because I forgot to do that last time*

**Version 3**

•*Added feature to change startup graphics per pack. File MUST be named "loading_splash.png" inside the resource directory. If none is found, automatically adjusts to the default.*
>After I set out to do most of what I want to accomplish i'm hoping to add these features to the pack editor so people actually know they exist

•*Actually made max video slider work properly. Max subliminals is still unfinished, but will be fixed next version (hopefully!)*
>Thank god! I spent double-digit hours trying to figure out how do to this the most gracefully (or at least efficiently) without rewriting the entire subprocess code, but in the end I opted for the easy/hacky way out. You'll see two new files appear in your edgeware directory, max_videos.dat, and max_subliminals.dat. These are files that only contain a single number, which is accessed and edited by the various popups to properly change the active number of popups. It's 4 AM right now and I want to push this before I forget, so right now only the video cap is fixed, but subliminals should be an easy addition now and will be done when I next work on EW++.

**Version 2**

•*Added feature to cap audio, and removed the hard-coded limit of 1 so multiple audio can play at the same time. The number goes down when audio finishes*
>I assume the intention of audio popups were things like long hypno files, which makes sense to limit to one. I wanted to expand this functionality to allow people to make packs that can layer shorter files, like layering multiple sex sounds on top of eachother. The default is still set to CAP ON with MAX 1 so if you are using old packs and don't want to touch this setting you don't have to do anything.

•*Added feature to cap videos in the config window, but is currently half implemented, so beware!*
>For specifics, the video capping feature works in the sense that it will cap the number of videos after a specific amount, but does NOT factor in video windows closing to lower the current videos playing count. I've been bashing my head against this problem for a while as it's much more complicated than other issues i've tackled in this project so far, but ended up wanting to take a break and finish/release some other elements of the program. I figured that since it technically "sort of" works and doesn't cause any instability or crashes (as far as i'm aware), I might as well include it in the release instead of commenting it out.

>If you want technical details, start.pyw calls popup.pyw as a subprocess, and passing variables to and from files like that is tricky (at least to me, with minimal python experience at time of writing). I've currently got start.pyw running a limiter "video number" variable that increases as it spawns new windows, but have struggled to find a way to get popup.pyw to reliably report back that a **video window** has closed and to get start.pyw to update the number whenever that happens. I will continue to try and figure out ways to do this without causing major performance/stability issues.

•*Moved the Subliminals option down to it's own section*

•*Added feature to give subliminals a percentage chance to activate. Defaults at 100, which is the same as the original EdgeWare*

•*Added option in the config menu to limit max number of subliminals, but it currently does nothing*
>Pretty much the exact same issue as the max video problem above, although this one might be easier to solve. However, unlike the max video slider, this truly does absolutely nothing and won't impact anything in the current version. I'm probably unprofessional for not disabling or removing this in the current version.

**Version 1.1**

•*Added change notes in about section*

**Version 1**

•*Added a option under "misc" to enable/disable desktop icon generation*

•*Old presets from the original edgeware still exist, but may have compatibility issues.*
