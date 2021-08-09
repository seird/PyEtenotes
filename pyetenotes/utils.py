import string


def center_widget(parent, widget):
    # Move the dialog to the center of the calling widget
    parent_pos = parent.pos()
    parent_size = parent.size()
    size = widget.size()
    widget.move(
        parent_pos.x() + parent_size.width() * 0.5 - size.width() * 0.5,
        parent_pos.y() + parent_size.height() * 0.5 - size.height() * 0.5
    )

def get_clean_string(s: str):
    disallowed = "\\/:*?\"<>|"
    return "".join(filter(lambda c: c not in disallowed, s))
