﻿# _ui_early.rpy: Contains code that absolutely must be parsed early.
# Since that is almost invariably I-Machine code, the rest of that is in here as well.
python early:

    config.save_directory = "katawashoujo_prealpha_new"

    # Defining own statements for the I-Machine here
    # see /common/00statements.rpy for details
    def parse_jump_in(l):
        is_expr = False
        firstword = l.word()
        if firstword == "expression":
            label = l.simple_expression()
            is_expr = True
        else:
            label = firstword
        if not label:
            renpy.error("parse error when evaluating custom jump")
        if l.rest():
            renpy.error("custom jump statement includes superfluous syntax: " + l.rest())
        return dict(label=label,is_expr=is_expr)

    def execute_jump_in(p):
        global save_name, last_scene_label
        if p["is_expr"]:
            label = eval(p["label"])
        else:
            label = p["label"]
        last_scene_label = label
        save_name = label
        scene_register(label)
        renpy.jump(label)

    def predict_jump_in(p):
        return []

    def next_jump_in(p):
        return p["label"]

    def lint_jump_in(p):
        label = p["label"]
        if not label:
            renpy.error("no target given to custom jump statement.")
        if not renpy.has_label(label) and not p["is_expr"]:
            renpy.error("custom jump to nonexistent label.")

    def execute_jump_out(p):
        global playthroughflag, mycontext, ss_desc
        nvl_clear()
        if not playthroughflag:
            replay_end()
        execute_jump_in(p)

    renpy.statements.register('jump_in',
                              parse=parse_jump_in,
                              execute=execute_jump_in,
                              predict=predict_jump_in,
                              lint=lint_jump_in,
                              next=next_jump_in)

    renpy.statements.register('jump_out',
                              parse=parse_jump_in,
                              execute=execute_jump_out,
                              predict=predict_jump_in,
                              lint=lint_jump_in,
                              next=next_jump_in)

    def replay_end():
        config.skipping = None
        renpy.scene()
        renpy.transition(config.main_game_transition)
        mycontext = "mm"
        ss_desc = ""
        wdt_off()
        renpy.music.stop(fadeout=0.5)
        renpy.music.play(music_menus, fadein=5.0, fadeout=0.5, if_changed=True)
        renpy.full_restart(label="invoke_scene_select")
        return

    # I-Machine stuff that doesn't actually need to be early but is kept in here to have it all in as few places as possible
    # Choice tokens. Actual values don't matter as long as they're unique
    m1, m2, m3, m4, m5, m6, m7, m8 = "1", "2", "3", "4", "5", "6", "7", "8"

    def replay_has_seen(label):
        # does not work because seen_label only works with jumps
        global playthroughflag
        return not playthroughflag and persistent_seen(label)

    def persistent_seen(label):
        return label in persistent.seen_labels

    def name_from_label(label):
        for (name, mylabel, display, path) in s_scenes:
            if mylabel == label:
                return name
        return False

    def wrap_label(label):
        # map "raw" scene label to scene block designation
        desired_target = persistent.current_language+"_"+label
        if renpy.has_label(desired_target):
            return desired_target
        else:
            return master_language+"_"+label

    def scene_register(inlabel):
        # mark scene as read. Is expected to get the raw label for convenience
        # modded - AKI WRITES SHITTY PYTHON CODE
        if not inlabel in persistent.seen_labels:
            persistent.seen_labels.append(inlabel)
        if not inlabel in seen_labels:
            if isinstance(inlabel, basestring) and len(store.seen_labels) >= 1:
                last = store.seen_labels[-1]
                i = inlabel
                if isinstance(last, tuple):
                    last = ''.join(last)
                if isinstance(i, tuple):
                    i = ''.join(last)
                if last != inlabel:
                    store.seen_labels.append(inlabel)
            elif len(seen_labels) == 0:
                store.seen_labels.append(inlabel)

    def seen_scene(label): # HA HA! I AM MAKING REALLIVE JOKES IN REN'PY GAME CODE!
        # if you don't understand what this does please for the love of rin don't edit this file
        return label in store.seen_labels

    def made_choice(label, choice):
        # a simple wrapper that lets you query past decisions
        return seen_scene((label, choice))

init python:
    if not persistent.seen_labels:
        persistent.seen_labels = []
    store.seen_labels = []

# the following three labels are I-Machine control code kept here for convenience.
label iscene (target):
    # the scene controller
    $ wdt_on()
    if playthroughflag:
        $ scene_register(target)
    $ last_visited_label = target
    if not notextmode:
        call expression wrap_label(target)
    $ wdt_off()
    return

label rinscene (target):
    # the scene controller for rins route
    if playthroughflag:
        $ scene_register(target)
    $ last_visited_label = target
    if not notextmode:
        call expression wrap_label(target)
    return

label hscene (target):
    # the scene controller
    $ scene_register(target)
    $ last_visited_label = target
    if not notextmode:
        if persistent.hdisabled:
            call scene_deleted
        else:
            call expression wrap_label(target)
    return

label imenu (target):
    # the menu controller
    $ wdt_on()
    $ scene_register(target)
    $ last_visited_label = target
    $ renpy.music.set_volume(0.3, 1.0, "music")
    $ renpy.music.set_volume(0.3, 1.0, "ambient")
    call expression wrap_label(target)
    $ renpy.music.set_volume(1.0, 1.0, "music")
    $ renpy.music.set_volume(1.0, 1.0, "ambient")
    $ scene_register((target,_return))
    $ renpy.block_rollback()
    $ wdt_off()
    return _return
    
label invoke_scene_select:
    $ renpy.call_in_new_context("_main_menu", "scene_select")