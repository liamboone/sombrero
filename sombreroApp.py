# -*- coding: utf-8 -*-
# Most of the sijax code has been modified from the chat and comet
# examples here:
# https://github.com/spantaleev/flask-sijax/tree/master/examples

import os, sys
import random
import pickle
import time, hashlib

path = os.path.join('.', os.path.dirname(__file__), '../')
sys.path.append(path)

import Automata
from shombrero import Sombrero

from flask import Flask, g, render_template
import flask_sijax

app = Flask(__name__)

app.config["SIJAX_STATIC_PATH"] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
app.config["SIJAX_JSON_URI"] = '/static/js/sijax/json2.js'

flask_sijax.Sijax(app)

class CometHandler(object):
    """A container class for all Sijax handlers."""

    @staticmethod
    def let_cmd(obj_response, varName, varExpr, data):
        if data == '':
            regs = {}
        else:
            regs = pickle.loads( data )
        regs[varName] = Sombrero( varExpr )
        regs[varName][1].Subset( regs[varName][1].Alphabet() )

        cmd = varName + " := " + varExpr
        print cmd
        obj_response = CometHandler.update_cmd(obj_response, cmd, regs)
        yield obj_response

    @staticmethod
    def eval_cmd(obj_response, varName, varExpr, data):
        if data == '':
            regs = {}
            return
        else:
            regs = pickle.loads( data )

        if varName not in regs:
            return

        accepted = regs[varName][1].Accepts( varExpr, False )
        sounds = ('do','de','da')
        for i in xrange(random.randint(3,7)):
            song = """
            <span class="song" id="note_%d" style="opacity: 0; position: relative; top: 0; left: -5;">
            %s
            </span>
            """ % (i, random.choice( sounds ))
            obj_response.html_append('#cmds',song)
            obj_response.script("$('#cmds').attr('scrollTop', $('#cmds').attr('scrollHeight'));")
            delay = random.randint(200,300)
            obj_response.script("$('#note_%d').animate({opacity: 1, top: %d, left: 0}, %d);" \
                                % (i, random.randint(-5,5), delay))
            yield obj_response
            time.sleep(delay/1000.0)

        obj_response.remove(".song")
        # Add cmd to the end of the container
        cmd = '%s %s "%s"' % (varName, ("accepts" if accepted else "rejects"), varExpr)
        obj_response = CometHandler.update_cmd(obj_response, cmd, regs)
        yield obj_response

    @staticmethod
    def update_cmd(obj_response, cmd, regs):
        obj_response.css('#cmds', 'border', '1px solid #e0e0e0')
        # Clear the textbox and give it focus in case it has lost it
        obj_response.attr('#varName', 'value', '')
        obj_response.attr('#varExpr', 'value', '')
        obj_response.script("$('#cmd').focus();")
        time_txt = time.strftime("%H:%M:%S", time.gmtime(time.time()))
        cmd_id = 'cmd_%s' % hashlib.sha256(time_txt).hexdigest()

        cmd = """
        <div id="%s" style="opacity: 0; position: relative; top: -5;">
            [<strong>%s</strong>] %s
        </div>
        """ % (cmd_id, time_txt, cmd)

        obj_response.html_append('#cmds', cmd)

        # Scroll down the cmds area
        obj_response.script("$('#cmds').attr('scrollTop', $('#cmds').attr('scrollHeight'));")

        # Make the new cmd appear in 400ms
        obj_response.script("$('#%s').animate({opacity: 1, top: 0}, 400);" % cmd_id)

        obj_response.attr('#cmds', 'data-exprs', pickle.dumps( regs ))
        return obj_response

    @staticmethod
    def save_cmd(obj_response, actName, varName, varExpr, data):
        cmd = ' '.join( [actName, varName, varExpr] )

        if actName == '' or varName == '' or varExpr == '':
            yield obj_response
            return

        if data == '':
            regs = {}
        else:
            regs = pickle.loads( data )

        if actName == "LET":
            regs[varName] = Sombrero( varExpr )
            regs[varName][1].Subset( regs[varName][1].Alphabet() )

        obj_response.css('#cmds', 'border', '1px solid #e0e0e0')
        # Clear the textbox and give it focus in case it has lost it
        obj_response.attr('#varName', 'value', '')
        obj_response.attr('#varExpr', 'value', '')
        obj_response.script("$('#cmd').focus();")

        time_txt = time.strftime("%H:%M:%S", time.gmtime(time.time()))
        cmd_id = 'cmd_%s' % hashlib.sha256(time_txt).hexdigest()

        if actName == "EVAL":
            accepted = regs[varName][1].Accepts( varExpr, False )
            sounds = ('do','de','da')
            for i in xrange(random.randint(3,7)):
                song = """
                <span class="song" id="note_%d" style="opacity: 0; position: relative; top: 0; left: -5;">
                %s
                </span>
                """ % (i, random.choice( sounds ))
                obj_response.html_append('#cmds',song)
                obj_response.script("$('#cmds').attr('scrollTop', $('#cmds').attr('scrollHeight'));")
                delay = random.randint(200,300)
                obj_response.script("$('#note_%d').animate({opacity: 1, top: %d, left: 0}, %d);" % (i, random.randint(-5,5), delay))
                yield obj_response
                time.sleep(delay/1000.0)
            obj_response.remove(".song")
            # Add cmd to the end of the container
            cmd = '%s %s "%s"' % (varName, ("accepts" if accepted else "rejects"), varExpr)

        cmd = """
        <div id="%s" style="opacity: 0; position: relative; top: -5;">
            [<strong>%s</strong>] %s
        </div>
        """ % (cmd_id, time_txt, cmd)

        obj_response.html_append('#cmds', cmd)

        # Scroll down the cmds area
        obj_response.script("$('#cmds').attr('scrollTop', $('#cmds').attr('scrollHeight'));")

        # Make the new cmd appear in 400ms
        obj_response.script("$('#%s').animate({opacity: 1, top: 0}, 400);" % cmd_id)

        obj_response.attr('#cmds', 'data-exprs', pickle.dumps( regs ))
        yield obj_response

    @staticmethod
    def clear_screen(obj_response):
        # Delete all cmds from the database

        # Clear the cmds container
        obj_response.html('#cmds', '')
        obj_response.css('#cmds', 'border', '0px')

        # Clear the textbox
        obj_response.attr('#cmd', 'value', '')

        # Ensure the texbox has focus
        obj_response.script("$('#cmd').focus();")

    @staticmethod
    def update_dfa(obj_response, dfa):
        pass

@flask_sijax.route(app, "/")
def index():
    if g.sijax.is_sijax_request:
        # The request looks like a valid Sijax request
        # Let's register the handlers and tell Sijax to process it
        g.sijax.register_comet_object(CometHandler)
        return g.sijax.process_request()

    return render_template('sombrero.html')

@app.route("/graph")
def graph():
    return render_template('graph.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port)
