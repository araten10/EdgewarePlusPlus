# Edgeware++

## What is EdgeWare?

Going to say immediately: **EdgeWare is not a virus, nor does it install itself onto your computer**. All it installs onto your computer by default is python 3.10 and a few extra libraries, which is needed for it to run. EdgeWare **can** potentially modify files on your computer, including deleting or replacing things, but these are all *user set* settings that are not on by default. That being said, other people can download EdgeWare, modify it to be malicious, and upload it elsewhere, so exercise caution when downloading versions from other sites. This project is open source, so feel free to peruse the source code if you're unsure.

Now, that all is pretty alarming stuff and seems a bit weird to preface the basic explanation with, but i'm fully aware the name "EdgeWare" doesn't inspire the most confidence for a program to be safe.

EdgeWare is a fetish-designed program (so 18+ only!!!) that essentially spawns popups over your screen in many different ways. These popups can include images, videos, audio, prompts (a sentence you have to repeat, think writing lines on a blackboard), etc. It's also highly customizable, with the ability to download "packs" people have made and use them yourself. Originally inspired by "Elsaware" (which, truthfully, I know nothing about), the original EdgeWare's goal was to be a "fake virus" program that looked like your computer was being taken over by porn. It can be ended at any time and also scheduled in ways to be used more passively. Even if you're not into "gooning" (having a kink for porn addiction/edging for a long time) I feel like EdgeWare is a pretty fun and interesting porn delivery system that allows you to see multiple images and videos at once without having to touch your keyboard or mouse.

PetitTournesol (EdgeWare's original creator) more or less took a hiatus and hasn't updated EdgeWare since 2022, which is totally valid. That being said, I felt like there were lots of things I personally wanted to see in the program. Inspired mostly by being mildly frustrated at deleting those dang desktop icons every time, I decided to start learning python and share the changes i've made. Thus EdgeWare++ was born, and as of writing this "new and improved" intro, there's over 10 new features to play around with. Some are quality of life updates, some are more fun things to tease yourself with. I'm generally trying to be as minimally intrusive to the original program as possible- my goal is complete both-ways pack compatibility with the old version of EdgeWare. I also don't want to remove any features (unless they were literally defunct), but I have moved some stuff around in the config menu to try and make more space.

"So how do I start using this darn thing?" Click the big ol' "code" button in the top right, then "download zip". Save and extract it somewhere, then run "EdgewareSetup.bat". This will install python 3.10 for you, if you don't already have it. After that it will give you instructions for further use, and open up "config.pyw" in the EdgeWare subfolder. From there you'll need an actual pack, which can be downloaded online or made yourself. Unfortunately at the time of writing there's really no congregated directory of packs everyone's made, they're all scattered to the four winds... but for a start [the original EdgeWare page](https://github.com/PetitTournesol/Edgeware) has a few sample packs, and i'm hoping to make a few myself to showcase the new features this extension can do.

**Any damage you do to your computer with EdgeWare is your own responsibility! Please read the "About" tab in the config window and make backups if you're planning on using the advanced, dangerous settings!**

The EdgeWare++ Pack Editor is now live [here](https://github.com/araten10/EdgewareEditor-PlusPlus).

## New Features In Edgeware++:

•*Toggle that switches from antialiasing to lanczos, if Edgeware wasn't displaying popups for you this will fix that! (probably)*

•*Toggle that allows you to play videos with VLC, which not only loads faster but also should fix audio issues*

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

## Planned Additions:

•*Dark Mode*

•*Giving mitosis a percentage activation slider*

•*Rewriting all the old config presets ~~to work with the new version~~, and a few new ones as well!* (turns out the old configs work fine (at least for me), but they could do with a little updating for new settings)

•*Allowing users to write config preset descriptions in the config window*

•*Allowing pack creators to somehow make Edgeware "change over time", for example, getting more depraved or having the themes change the longer it runs. Would likely use the mood system.*

•*Making a demo video/images so people can get an idea of what they're downloading ~~but this might take a while since it requires me to clean my desktop~~*

•*Making some new demo packs showcasing added features, allows me to not only show off my work but also be a horny bastard and browse porn*

I'm also wanting to add features to the pack editor, will probably do that when this is in a state where I feel mostly done with what I wanted to accomplish.

**Suggestions**

Suggestions I got from people who used the software and I thought would be interesting enough to try. Lower priority than my own planned additions, but still something I hope to add (or attempt to) in the future!

•*New type of popup: full screen text, taken from caption file. Like subliminals but briefly flashing on full screen.*

•*Randomized settings button. Might implement when i'm mostly done adding new config vars, but also gave me the idea for pack creators to be able to make "recommended settings" that you can switch to in the pack info tab*

•*Support for confining edgeware to a single monitor, which actually sounds like a really good idea but i'd want to test it on a few monitor setups and it sounds fairly technical*

•*More "classic virus"-y popup options, like [moving popups](https://www.youtube.com/watch?v=LSgk7ctw1HY)*

## EdgeWare++ Patch Notes
**If you see that there's a new update and are somebody (like me) who is lazy and doesn't like installing every single update if unnecessary, here is how I do versioning:**

•+1.0 to version number: multiple new features, or a single large feature

•+0.5-0.25 to version number: new feature, but a smaller one or something not as essential, or lots of bugfixes

•+0.2-0.1 to version number: very small update, usually just a bugfix, accessibility options, UI tweaks

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
