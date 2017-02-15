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
    # FIXME:  need to set/handle char encoding; Sp. 'í' was enough to break it
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
    def get(self, error="", title="", body=""):
        logging.info("get() for NewBlogPost...")
        t = jinja_env.get_template("new_post.html")
        error = self.request.get("error")
        content = t.render(error = error, title = title, body = body)
        self.response.write(content)

    def post(self):
        have_error = False
        logging.info("post() for NewBlogPost")
        title_str = self.request.get("title").lstrip().rstrip()
        body_str = self.request.get("body").lstrip().rstrip()
        
        if len(title_str) == 0 or len(body_str) == 0:
            have_error = True

        if have_error != True:
            logging.info("TODO:  create new entity and put() to DB")
            title = cgi.escape(title_str)
            blog_entry = cgi.escape(body_str)
            b = BlogPost(title = title, blog_entry = blog_entry)
            key = b.put()
            time.sleep(1) # to ensure record's stable before grabbing id
            b.permalink_id = str(key.id())  # FIXME: is "b." OK on RHS?
            b.put()
            logging.info('Wrote new BlogPost entry to DB:' +
                            '  title = ' + b.title + 
                            ', permalink = ' + str(b.permalink_id))
                            # '  id = ' + str(key.id()) +
            self.redirect("/blog")

        else:
            logging.info("title and/or entry bad")
            error=cgi.escape('Need both title and body for new blog post.')
            escaped_title = cgi.escape(title_str)
            escaped_body = cgi.escape(body_str)
            self.redirect("/blog/newpost", error, escaped_title, escaped_body)
        

temp_blogs_data = { 
    'Blogs r Us': 'It was the best of times; it was the',
    'Second Blog Post': 'I hear the third time\'s the charm'
}

class ViewAllBlogPostsHandler(Handler):
    def get(self):
        # num_existing_recs = BlogPost.all().count
        
        # controls adding dummy starter BlogPost entries/data
        # db_was_empty = True
        
        all_blogs = []
        
        # FIXME:  replace magic number in LIMIT clause
        query_iterator = db.GqlQuery("SELECT * FROM BlogPost" +
                                " ORDER BY created DESC LIMIT 5").run()
        for blog_item in query_iterator:
            db_was_empty = False
            # ", permalink = " + str(blog_item.permalink_id) +
            logging.info("item created: " + str(blog_item.created) +
                            ", title = " + unicode(blog_item.title))
            # all_blogs.insert(0, blog_item)
            all_blogs.append(blog_item)

        '''
        if db_was_empty:
            for blog_item in temp_blogs_data:
                title = cgi.escape(blog_item)
                blog_entry = cgi.escape(temp_blogs_data[blog_item])
                b = BlogPost(title = title, blog_entry = blog_entry)
                all_blogs.insert(0, b)  # FIXME:  zero index SHOULD've worked
                key = b.put() 
                logging.info('Wrote another BlogPost entry to DB:' + 
                                '  title = ' + b.title + str(b) +
                                '  id = ' + str(key.id()))
                                # '  key = ' + str(key))
                time.sleep(1) # to ensure record's stable before grabbing id
                b.permalink_id = str(key.id())
                b.put()
                time.sleep(1) # to ensure unique timestamps for blog entries
        '''
        
        t = jinja_env.get_template("bloghomepage.html")
        content = t.render(blog_posts = all_blogs)
        self.response.write(content)

    def post(self):
        logging.info("post() for/on main blog page")
        pass
        

class ViewSingleBlogPostHandler(Handler):
    def get(self, id):
        self.response.write("HERE, we would view blog post w/ID = " + id)


app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/blog', ViewAllBlogPostsHandler),
    ('/blog/newpost', NewBlogPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewSingleBlogPostHandler)
], debug=True)
