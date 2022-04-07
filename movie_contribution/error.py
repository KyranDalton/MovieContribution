from flask import render_template

def page_not_found_error(e):
    """
    Handles requests to unknown pages
    showing a more useful error message
    """
    return render_template('404.html'), 404
