title: Useful Avrae Aliases
category: D&D
tags: Avrae

[Avrae](https://avrae.io/) is a Discord bot that makes running and playing D&D play-by-post games much easier—it provides useful tools such as integration with [D&D Beyond](https://www.dndbeyond.com/), powerful dice-rolling options, and combat initiative tracking.

However, there are some things it doesn't do well natively. For this, it provides a powerful scripting API via [aliases and snippets](https://avrae.readthedocs.io/en/latest/aliasing/aliasing.html) for you to extend its functionality with your own commands. Many people have written their own, and these are a few of the custom commands that we have set up in our games to make life just a little bit easier.

To use any of these aliases, paste the text in the code blocks below into a DM with Avrae (or any channel they are a member of).

## Quick Character Switcher

When you link a character from D&D Beyond, Avrae will remember it and allow you to use the character in combat and for ability checks, etc. However, if you're playing in multiple games, you have to constantly remember to change the active character to the correct one before continuing. We found a handy alias on the Avrae Developer's Discord for assigning characters to channels, so instead of remembering that "in this channel, I'm Kaith, but in this channel, I'm Elmer", you can just run `!ch` to switch to the right character for that game. I'm reproducing that here (tweaked for a recent Avrae update that deprecated a couple of the commands):

```python
!alias ch {{c,id,a,m,n,h,H,w,R=load_json(chars) if exists('chars') else {}, {'c':str(ctx.channel.id),'s':str(ctx.guild.id if ctx.guild else "")} ,&ARGS&[1:],&ARGS&[:1] or 0,'\n','- This Channel','- This Server' ,'',"%x"%roll('1d16777216')}}{{m=(1 if m[0] in 'add'  else 2 if m[0] in 'delete'  else 3 if m[0] in 'roster' else 4 if m[0] in 'help?' else 0) if m else 0}}{{x=not m or ((a[1] if a[1].isdigit() else id.c if a[1] in 'chan' else id.s) if a and len(a)>1 else id.s)}}{{X=not m or ((a[0] if a[0].isdigit() else id.c if a[0] in 'chan' else id.s) if a else id.s)}}{{name=c.get(X)}}{{emb=f' -title "Quick Character Changer" -footer "!ch [help|?] - Bring up the help window" -color {R} '}}{{A=''.join([c[i] for i in c if i==id.c][:1]) or ''.join([c[i] for i in c if i==id.s][:1])}}{{add=not m==1 or not  a or c.update({x:a[0]}) or set_uvar('chars',dump_json(c)) or a[0]}}{{delete=not m==2 or not c.pop(X) or not set_uvar('chars', dump_json(c)) or X}}{{"embed "+emb+(f'-t 10 -desc "Added `{add}` to ID `{x}`."' if (m==1 and a) else f'-t 10 -desc "{"No char found for ID" if not name else f"Removed `{name}` with ID"} `{X}`."' if m==2 else f'-t 20 -f "Roster| {n+(n.join([f"`{i}` - `{c[i]} ` {h if i in id.c else H if id.s and i in id.s else w} " for i in c]) or "*None*")}"' if m==3 else f'-f "!ch|Changes to the appropriate character for the channel/server." -f "!ch roster|View a list of all channel/server id\'s and the character they will load" -f "!ch add <name> [chan⏐id]|Adds `name` to the selected id. Default is server id, `chan` selects the channel id, or you can input the channel/server id manually" -f "!ch delete [chan⏐id]|Deletes the given id. Default is server id, `chan` selects the channel id, or you can input the channel/server id manually" -f "Current ID\'s|`Channel` - `{id.c}`{n}`Server` - `{id.s}`"') if m else (f"char {A}" if A else "embed -t 5 -desc 'Channel not found in list'"+emb)}}
```

With that alias set, you can run `!ch add [character] chan` to assign the provided character to the current channel. Now, when you switch channels, you just have to run `!ch` to activate the right one.

However, remembering to run `!ch` is easier said than done. How many times have I switched to a channel and run `!g lr` to give my character a long rest, before realising that I hadn't switched and had just given one of my other characters a poorly-timed rest instead? To solve this, we put together an alias (worked out mostly by my friend [Madi](https://www.flexpotential.com/)) designed to prefix any command you may want to run, that automatically switches before executing the actual command you asked for:

```python
!alias x multiline
<drac2>
id={'c':str(ctx.channel.id),'s':str(ctx.guild.id if ctx.guild else "")}
c = load_json(chars) if exists('chars') else {}
n ='\n'
A= ''.join([c[i] for i in c if i==id.c][:1]) or ''.join([c[i] for i in c if i==id.s][:1])
return f'!char {A}'
</drac2>
!&*&
```

For me it's aliased to `x`, just to make it quick and easy to type. `!x check str` will always do a strength check for the right character for the game in *this* channel. `!x g lr` will always give the correct character a long rest. In combination with the `!ch` alias, this is probably the most handy alias I have set up—I only have to remember to always use `!x ` instead of `!`, and it always just does the right thing.

## Feat Spells

The other problem we frequently run into is using spells provided by feats. There are many feats that provide the with character additional spells; one's they're able to cast a particular number of times between rest, without using up spell slots. A good example is the [Magic Initiate](https://www.dndbeyond.com/feats/magic-initiate) feat:

> Choose a class: bard, cleric, druid, sorcerer, warlock, or wizard. You learn two cantrips of your choice from that class's spell list.
>
> - In addition, choose one 1st-level spell from that same list. You learn that spell and can cast it at its lowest level. Once you cast it, you must finish a long rest before you can cast it again using this feat.

Avrae only partially understands these. Pulling from D&D Beyond, it creates a custom counter for each spell you've learned, with the correct number of "bubbles" for the amount of times you can use it, such as the example in the screenshot below:

![Avrae custom counter output showing Magic Initiate - Command counter](/assets/avrae-1.png)

Here, Scrat (my Hadozee character) has the **Magic Initiate (Cleric): Command** counter, that corresponds to his background feat providing that 1-st level spell. Avrae's also added the spell to Scrat's spellbook (`!sb`), meaning Scrat is able to cast it. However, they're not linked together in any way. Casting the spell uses a spell slot (it shouldn't) and doesn't update the counter (it should). This means that instead, there are a number of things I need to remember to do when casting the spell:

* Firstly, check the custom counter to see if it's been used or not (i.e. is the spell available to me, or do I need a long rest first).
* Cast the spell without using a spell slot (the `-i` flag to `!cast` or `!i cast` will do this).
* Decrement the counter.

To solve this, I wrote a short alias I call `!featcast`, which can be used in place of `!cast` (or `!i cast`) to handle the above three things:

```python
!alias featcast {{a=&ARGS&}}{{H=not a or "help" in a or "?" in a}}{{s,r=H or a[0],H or " ".join(a[1:])}}multiline
<drac2>
if not H:
    ch=character()
    s=s.lower()
    ccs=[x for x in ch.consumables if ":" in x.name and (x.name.split(":")[1].lower().endswith(s.lower()) or x.name.split(": ")[1].lower().startswith(s.lower()))]
    cc=ccs[0] if ccs else None
    if cc:
        t,n=[x.strip() for x in cc.name.split(":")]
        if cc.value > 0:
            i=""
            if combat():
                i="i "
            cc.set(cc.value-1)
            return f"!{i}cast '{n}' -i {r}"
        else:
            return f"!embed -title 'Cannot cast {n}!' -desc '{ch.name} does not have any uses of {n} from the {t} feat available.\n\n**{cc.name}**\n{cc}'"
    else:
        return f"!embed -title 'Could not find a \"{s}\" custom counter' -desc 'Check that your feats for **{ch.name}** are set up correctly.' -thumb <image>"
else:
    return f"!embed -title 'Help for feat-casting' -desc 'Use `!featcast <spell>` to cast a spell provided by a feat, instead of using your spell slots.'"
</drac2>
```

It relies on the fact that Avrae names the custom counters sensibly, in the format of "Feat Name: Spell Name". When typing `!featcast command -t Target1 -t Target2`, it will look for a custom counter named in that way that could possibly match the provided spell name. When it finds one, it checks for a free slot, and casts the spell (with the provided arguments), decrementing the counter.

There are many feats and backgrounds that provide spells, and this alias has made handling them *much* easier. Hopefully it can be of some use in your games too!
