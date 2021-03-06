#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk

from pisi.db.groupdb import GroupDB


class ScGroupButton(Gtk.Button):
    """ Manage the monotony of a Group """

    group = None

    def __init__(self, db, group):
        Gtk.Button.__init__(self)

        self.group = group

        icon_theme = self.get_settings().get_property("gtk-icon-theme-name")
        icon_theme = icon_theme.lower().replace("-", "")
        # Sneaky, I know.
        if icon_theme == "arcicons" or icon_theme == "arc":
            devIcon = "text-x-changelog"
        else:
            devIcon = "gnome-dev-computer"

        replacements = {
            "text-editor": "x-office-calendar",
            "redhat-programming": devIcon,
            "security-high": "preferences-system-privacy",
            "network": "preferences-system-network",
        }

        # Pretty things up with a Icon|Label setup
        icon = str(group.icon)
        if icon in replacements:
            icon = replacements[icon]

        gDesc = str(group.localName)
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG)
        image.set_halign(Gtk.Align.START)
        image.set_pixel_size(64)

        label_box = Gtk.VBox(0)

        box = Gtk.HBox(0)
        box.pack_start(image, False, False, 0)
        image.set_property("margin-right", 10)
        label = Gtk.Label(gDesc)
        label.get_style_context().add_class("title")
        label.set_halign(Gtk.Align.START)
        label.set_valign(Gtk.Align.START)
        label_box.pack_start(label, True, True, 0)
        box.pack_start(label_box, True, True, 0)
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.add(box)

        # count the components
        kids = db.get_group_components(group.name)
        info_label = Gtk.Label("%s sections" % len(kids))
        info_label.set_halign(Gtk.Align.START)
        info_label.get_style_context().add_class("info-label")
        info_label.get_style_context().add_class("dim-label")
        label_box.pack_start(info_label, False, False, 0)

        self.get_style_context().add_class("group-button")


class ScGroupsView(Gtk.EventBox):
    """ Main group view, i.e. "System", "Development", etc. """

    flowbox = None
    groupdb = None
    group_names = None
    scroll = None
    stack = None
    owner = None

    group_map = dict()

    # Main component view
    comp_view = None

    def handle_back(self):
        """ Go back to the group selection view for now """
        self.stack.set_visible_child_name("groups")
        self.owner.set_can_back(False)

    def can_back(self):
        """ Whether we can go back """
        return self.stack.get_visible_child_name() != "groups"

    def __init__(self, owner):
        Gtk.EventBox.__init__(self)
        self.owner = owner

        self.stack = Gtk.Stack()
        t = Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        self.stack.set_transition_type(t)
        self.add(self.stack)

        self.scroll = Gtk.ScrolledWindow(None, None)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        self.stack.add_named(self.scroll, "groups")

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_property("margin-start", 40)
        self.flowbox.set_property("margin-end", 40)
        self.flowbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_valign(Gtk.Align.START)
        self.scroll.add(self.flowbox)

        # Consider making this guy global.
        self.groupdb = GroupDB()

        st = self.get_style_context()
        st.add_class(Gtk.STYLE_CLASS_VIEW)
        st.add_class("content")

        self.comp_view = Gtk.VBox(0)
        self.stack.add_named(self.comp_view, "components")
        self.init_view()

    def on_group_clicked(self, btn, data=None):
        print btn.group.name
        self.stack.set_visible_child_name("components")
        self.owner.set_can_back(True)

    def init_view(self):
        """ Set up the groups and push them into the view """
        for widget in self.flowbox.get_children():
            widget.destroy()

        self.group_names = sorted(self.groupdb.list_groups())
        self.group_map = dict()

        # set up the group widgets
        for name in self.group_names:
            group = self.groupdb.get_group(name)
            self.group_map[name] = group

            button = ScGroupButton(self.groupdb, group)
            button.connect("clicked", self.on_group_clicked)
            button.show_all()
            self.flowbox.add(button)
