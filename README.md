SysPropChart2
===

v 1.2 dec 3 2019


This addon allows you to make presets for the properties you need to change or view often, and it lets you view the properties of multiple selected objects.

Use commas in the property string as a delimiter so you can expose multiple properties of the same object.

When objects of multiple types are selected, there may be failures in the algorithm to display, if a property is referenced that does not belong to all type of objects.  So for example, objects have a 'color' property that is not usually the one that is wanted.  'data.color' is more likely in the case of a light, for example.  (I'm not sure what object 'color' even does in that case...)  When referencing to display the color of selected lights, by putting 'data.color' in the syspropchart box, having mesh objects selected then gets you errors in the console about rna_uiItemR: property not found: Mesh.color. This is to be expected.


[syspropchart2 as zip](https://github.com/dustractor/syspropchart2/releases/download/1.2/syspropchart2.zip)

A property, in blender terms, is something that is editable in the interface.  If you have 'show python tooltips' enabled in blender's preferences, then you may have noticed these names when you hover over various parts of the interface.

The original addon, System Property Chart, allowed for entering a string such as:

    name,data.name

And then while having one or more objects selected, the addon would put a text field for the object name and the name of the data it contained.

Unfortunately some properties are impossible to access via the algorithms used in the original addon.  This one lets you access properties even if you need to use keyed["access"] for properties in named collections and also you may access elements of an indexed collection likes[0] ...

There is also the possibility for interpolation across vectors, floats, and most color properties.

---

roadmap 2020

get some better presets

hide the interpolation buttons unless wanted

make interpolation assess first and last of selection and make set a batch on other types like enum or bool

change the grouping and make option to not group by prop (i had it that way but the bl ui drag-across-thing would not work unless the interface were more spreadsheetlike

rewrite this readme ditch the tude

ok oll korrect for now gud luk blenderhead


