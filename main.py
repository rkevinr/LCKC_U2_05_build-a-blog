#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import jinja2
from google.appengine.ext import db

import cgi
import logging
import os
import time


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))


class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    blog_entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    permalink_id = db.StringProperty(required = False)


class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.  """
    def renderError(self, error_code):
        """ Sends an HTTP error code + generic 'oops!' message to the client."""
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


class IndexHandler(Handler):
    def get(self):
        self.redirect('/blog')


class NewBlogPostHandler(Handler):
    def render_page(self, error="", title="", body=""):
        logging.info("render_page() for NewBlogPost...")
        t = jinja_env.get_template("new_post.html")
        content = t.render(error=error, title=title, body=body)
        self.response.write(content)

    def get(self, error="", title="", body=""):
        logging.info("get() for NewBlogPost...")
        t = jinja_env.get_template("new_post.html")
        error = self.request.get("error")
        content = t.render(error=error, title=title, body=body)
        self.response.write(content)

    def post(self):
        have_error = False
        logging.info("post() for NewBlogPost")
        title_str = self.request.get("title").lstrip().rstrip()
        body_str = self.request.get("body").lstrip().rstrip()
        
        if len(title_str) == 0 or len(body_str) == 0:
            have_error = True

        if have_error != True:
            title = cgi.escape(title_str)
            blog_entry = cgi.escape(body_str)
            b = BlogPost(title = title, blog_entry = blog_entry)
            key = b.put()
            time.sleep(1) # to ensure record's stable before grabbing id
            b.permalink_id = str(key.id())
            b.put()
            self.redirect("/blog/" + b.permalink_id)

        else:
            logging.info("title and/or entry bad")
            error=cgi.escape('Need both title and body for new blog post.')
            escaped_title = cgi.escape(title_str)
            escaped_body = cgi.escape(body_str)
            self.render_page(error=error, title=escaped_title,
                                body=escaped_body)
        

temp_blogs_data = { 
    'Blogs r Us': 'It was the best of times; it was the',
    'Second Blog Post': 'I hear the third time\'s the charm'
}

class ViewAllBlogPostsHandler(Handler):
    def get(self):
        all_blogs = []
        MAX_BLOG_ENTRIES_PER_PAGE = str(5)
        
        query_iterator = db.GqlQuery("SELECT * FROM BlogPost" +
                                " ORDER BY created DESC LIMIT " +
                                MAX_BLOG_ENTRIES_PER_PAGE).run()
        
        for blog_item in query_iterator:
            all_blogs.append(blog_item)

        t = jinja_env.get_template("bloghomepage.html")
        content = t.render(blog_posts = all_blogs)
        self.response.write(content)


class ViewSingleBlogPostHandler(Handler):
    def render_page(self, title="", body=""):
        t = jinja_env.get_template("display_indiv_post.html")
        content = t.render(title=title, body=body)
        self.response.write(content)
        
    def get(self, id=""):
        blog_item = BlogPost.get_by_id(int(id))

        if blog_item:
            title=blog_item.title
            body=blog_item.blog_entry
            self.render_page(title=title, body=body)
        else:
            self.redirect("/blog")  # FIXME:  should post ERROR if id is bogus


app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/blog', ViewAllBlogPostsHandler),
    ('/blog/newpost', NewBlogPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewSingleBlogPostHandler)
], debug=True)
