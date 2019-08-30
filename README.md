SysPropChart2
===


A property, in blender terms, is something that is editable in the interface.  If you have 'show python tooltips' enabled in blender's preferences, then you may have noticed these names when you hover over various parts of the interface.

The original addon, System Property Chart, allowed for entering a string such as:

    name,data.name

And then while having one or more objects selected, the addon would put a text field for the object name and the name of the data it contained.

Unfortunately some properties are impossible to access via the algorithms used in the original addon.  This one lets you access properties even if you need to use keyed["access"] for properties in named collections and also you may access elements of an indexed collection likes[0] ...

And there is interpolation.  For vectors, floats, and most color properties.

So if you want to interpolate the color of your fifth Diffuse BSDF node of whatever material is in the third slot of every object:

    data.materials[2].node_tree.nodes["Diffuse BSDF.004"].inputs[0].default_value

Knock yourself out.

Make presets for the things you need to change or view often, and use commas in the property string as a delimiter so you can expose multiple properties of the same object.

