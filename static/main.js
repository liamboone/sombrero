//
//  main.js
//
//  A project template for using arbor.js
//

(function($){

    var Renderer = function(canvas){
        var canvas = $(canvas).get(0)
        var ctx = canvas.getContext("2d");
        var particleSystem

        var that = {
            init:function(system){
                //
                // the particle system will call the init function once, right before the
                // first frame is to be drawn. it's a good place to set up the canvas and
                // to pass the canvas size to the particle system
                //
                // save a reference to the particle system for use in the .redraw() loop
                particleSystem = system

                // inform the system of the screen dimensions so it can map coords for us.
                // if the canvas is ever resized, screenSize should be called again with
                // the new dimensions
                particleSystem.screenSize(canvas.width, canvas.height) 
                particleSystem.screenPadding(80) // leave an extra 80px of whitespace per side

                // set up some event handlers to allow for node-dragging
                that.initMouseHandling()
            },

            redraw:function(){
                // 
                // redraw will be called repeatedly during the run whenever the node positions
                // change. the new positions for the nodes can be accessed by looking at the
                // .p attribute of a given node. however the p.x & p.y values are in the coordinates
                // of the particle system rather than the screen. you can either map them to
                // the screen yourself, or use the convenience iterators .eachNode (and .eachEdge)
                // which allow you to step through the actual node objects but also pass an
                // x,y point in the screen's coordinate system
                // 
                ctx.fillStyle = "white"
                ctx.fillRect(0,0, canvas.width, canvas.height)

                particleSystem.eachEdge(function(edge, pt1, pt2){
                    // edge: {source:Node, target:Node, length:#, data:{}}
                    // pt1:  {x:#, y:#}  source position in screen coords
                    // pt2:  {x:#, y:#}  target position in screen coords

                    // draw a line from pt1 to pt2
                    ctx.strokeStyle = "rgba(0,0,0, .333)"
                    ctx.fillStyle = "rgba(0,0,0, .733)"
                    ctx.lineWidth = 3
                    var headlen = 10;   // length of head in pixels
                    if( pt1.x == pt2.x && pt1.y == pt2.y )
                    {
                        var angle1 = -Math.PI/2-0.5
                        var angle2 = -Math.PI/2+0.5
                        var pt1x = pt1.x+Math.cos(angle1)*20
                        var pt1y = pt1.y+Math.sin(angle1)*20
                        var pt2x = pt1.x+Math.cos(angle2)*30
                        var pt2y = pt1.y+Math.sin(angle2)*30
                        
                        var cpt1x = pt1.x+Math.cos(angle1)*80
                        var cpt1y = pt1.y+Math.sin(angle1)*80
                        var cpt2x = pt1.x+Math.cos(angle2)*80
                        var cpt2y = pt1.y+Math.sin(angle2)*80
                        ctx.beginPath()
                        ctx.moveTo(pt1x,pt1y)
                        ctx.bezierCurveTo(cpt1x, cpt1y, cpt2x, cpt2y, pt2x, pt2y)
                        ctx.stroke()
                        ctx.beginPath()
                        pt2x = pt2.x+Math.cos(angle2)*20
                        pt2y = pt2.y+Math.sin(angle2)*20
                        ctx.moveTo(pt2x, pt2y)
                        ctx.lineTo(pt2x+Math.cos(angle2+0.5)*headlen, pt2y+Math.sin(angle2+0.5)*headlen)
                        ctx.lineTo(pt2x+Math.cos(angle2-0.5)*headlen, pt2y+Math.sin(angle2-0.5)*headlen)
                        ctx.lineTo(pt2x, pt2y)
                        ctx.fill()
                        ctx.font = "bold 11px Arial"
                        ctx.textAlign = "center"
                        ctx.fillText( edge.data.label, pt1.x, pt1.y-60 )
                    }
                    else
                    {
                        var angle = Math.atan2(pt1.y-pt2.y,pt1.x-pt2.x);
                        var perp = angle + 0.5*Math.PI
                        var angle1 = angle - 0.5
                        var angle2 = angle + 0.5
                        var pt1x = pt1.x-Math.cos(angle)*20+Math.cos(perp)*5
                        var pt1y = pt1.y-Math.sin(angle)*20+Math.sin(perp)*5
                        var pt2x = pt2.x+Math.cos(angle)*20+Math.cos(perp)*5
                        var pt2y = pt2.y+Math.sin(angle)*20+Math.sin(perp)*5
                        ctx.beginPath()
                        ctx.moveTo(pt1x, pt1y)
                        ctx.lineTo(pt2x+Math.cos(angle)*headlen*0.91, pt2y+Math.sin(angle)*headlen*0.9)
                        ctx.stroke()
                        ctx.beginPath()
                        ctx.moveTo(pt2x, pt2y)
                        ctx.lineTo(pt2x+Math.cos(angle1)*headlen, pt2y+Math.sin(angle1)*headlen)
                        ctx.lineTo(pt2x+Math.cos(angle2)*headlen, pt2y+Math.sin(angle2)*headlen)
                        ctx.lineTo(pt2x, pt2y)
                        ctx.fill()
                        ctx.font = "bold 11px Arial"
                        ctx.textAlign = "center"
                        pt1x = pt2.x+Math.cos(angle)*35+Math.cos(perp)*12
                        pt1y = pt2.y+Math.sin(angle)*35+Math.sin(perp)*12
                        ctx.fillText( edge.data.label, pt1x, pt1y+4 )
                    }
                })

                particleSystem.eachNode(function(node, pt){
                    // node: {mass:#, p:{x,y}, name:"", data:{}}
                    // pt:   {x:#, y:#}  node position in screen coords

                    // draw a rectangle centered at pt
                    var w = 50
                    ctx.beginPath()
                    ctx.fillStyle = "black"
                    ctx.strokeStyle = "black"
                    ctx.lineWidth = 2
                    ctx.arc(pt.x, pt.y, 20, 0, 2*Math.PI, false)
                    ctx.stroke()
                    if( node.data.accepting )
                    {
                        ctx.beginPath()
                        ctx.arc(pt.x, pt.y, 25, 0, 2*Math.PI, false)
                        ctx.stroke()
                    }
                    ctx.font = "bold 11px Arial"
                    ctx.textAlign = "center"
                    ctx.fillText( node.data.label, pt.x, pt.y+4 )
                    //ctx.fillRect(pt.x-w/2, pt.y-w/2, w,w)
                })    			
            },

            initMouseHandling:function(){
                // no-nonsense drag and drop (thanks springy.js)
                var dragged = null;

                // set up a handler object that will initially listen for mousedowns then
                // for moves and mouseups while dragging
                var handler = {
                    clicked:function(e){
                        var pos = $(canvas).offset();
                        _mouseP = arbor.Point(e.pageX-pos.left, e.pageY-pos.top)
                        dragged = particleSystem.nearest(_mouseP);

                        if (dragged && dragged.node !== null){
                            // while we're dragging, don't let physics move the node
                            dragged.node.fixed = true
                        }

                        $(canvas).bind('mousemove', handler.dragged)
                        $(window).bind('mouseup', handler.dropped)

                        return false
                    },
                    dragged:function(e){
                        var pos = $(canvas).offset();
                        var s = arbor.Point(e.pageX-pos.left, e.pageY-pos.top)

                        if (dragged && dragged.node !== null){
                            var p = particleSystem.fromScreen(s)
                            dragged.node.p = p
                        }

                        return false
                    },

                    dropped:function(e){
                        if (dragged===null || dragged.node===undefined) return
                        if (dragged.node !== null) dragged.node.fixed = false
                        dragged.node.tempMass = 1000
                        dragged = null
                        $(canvas).unbind('mousemove', handler.dragged)
                        $(window).unbind('mouseup', handler.dropped)
                        _mouseP = null
                        return false
                    }
                }

                // start listening
                $(canvas).mousedown(handler.clicked);

            },

        }
        return that
    }    

    $(document).ready(function(){
        var sys = arbor.ParticleSystem(1000, 600, 0.5) // create the system with sensible repulsion/stiffness/friction
        sys.parameters({gravity:true}) // use center-gravity to make the graph settle nicely (ymmv)
        sys.renderer = Renderer("#viewport") // our newly created renderer will have its .init() method called shortly by sys...

        // add some nodes to the graph and watch it go...
        sys.addNode('0', {label:"0"})
        sys.addNode('1', {label:"1"})
        sys.addNode('2', {label:"2"})
        sys.addNode('3', {label:"3"})
        sys.addNode('4', {accepting:true, label:"4"})
        
        sys.addEdge('0','1', {label:"a"});sys.addEdge('0','2', {label:"b"});
        sys.addEdge('1','1', {label:"a"});sys.addEdge('1','3', {label:"b"});
        sys.addEdge('2','1', {label:"a"});sys.addEdge('2','2', {label:"b"});
        sys.addEdge('3','1', {label:"a"});sys.addEdge('3','4', {label:"b"});
        sys.addEdge('4','1', {label:"a"});sys.addEdge('4','2', {label:"b"});

        // sys.graft({
        //   nodes:{
        //     f:{alone:true, mass:.25}
        //   }, 
        //   edges:{
        //     a:{ b:{},
        //         c:{},
        //         d:{},
        //         e:{}
        //     }
        //   }
        // })

    })

})(this.jQuery)
