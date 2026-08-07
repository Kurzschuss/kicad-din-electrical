// ProjectOS / kicad-din-electrical
// Herstellerneutrales MCB-1P-Referenzmodell
// Von Grund auf neu erstellt; keine Hersteller-CAD-Geometrie übernommen.
// Alle Maße in mm.

$fn = 48;

// Prototypmaße für den KiCad-Praxistest.
module_width = 18.0;
module_length = 84.0;   // inklusive neutral abstrahierter Schraubklemmen
body_depth = 70.0;

front_step_width = 14.0;
front_step_length = 46.0;
front_step_height = 18.0;

toggle_width = 10.0;
toggle_length = 18.0;
toggle_height = 8.0;
toggle_angle = -12;

terminal_width = 10.0;
terminal_length = 12.0;
terminal_recess_depth = 8.0;

// KiCad-/PCB-Koordinatensystem:
// X = Modulbreite (18 mm Raster)
// Y = Gerätelänge in der Draufsicht (84 mm)
// Z = Höhe über der Platine
// Ursprung = geometrische Mitte der Draufsicht auf der PCB-Ebene.

module rounded_box_xy(size=[1,1,1], radius=1.0) {
    translate([-size[0]/2 + radius, -size[1]/2 + radius, radius])
        minkowski() {
            cube([size[0]-2*radius, size[1]-2*radius, size[2]-2*radius], center=false);
            sphere(r=radius);
        }
}

module housing() {
    difference() {
        rounded_box_xy([module_width, module_length, body_depth], 1.0);

        // Neutral abstrahierte Anschlussöffnungen an beiden Stirnseiten.
        for (sy = [-1, 1]) {
            translate([0, sy*(module_length/2-terminal_length/2), body_depth-terminal_recess_depth/2])
                cube([terminal_width, terminal_length, terminal_recess_depth+0.2], center=true);
        }
    }
}

module front_step() {
    translate([0, 0, body_depth-0.5])
        rounded_box_xy([front_step_width, front_step_length, front_step_height], 0.8);
}

module toggle() {
    translate([0, 0, body_depth + front_step_height - 1.0])
        rotate([toggle_angle, 0, 0])
            rounded_box_xy([toggle_width, toggle_length, toggle_height], 0.8);
}

module terminal_collar(y0) {
    translate([0, y0, body_depth-2.0])
        difference() {
            rounded_box_xy([module_width-5.0, 10.0, 8.0], 0.7);
            translate([0, 0, 4.0])
                cylinder(h=8.2, d=4.0, center=true);
        }
}

module mcb_1p() {
    union() {
        housing();
        front_step();
        toggle();
        terminal_collar(-(module_length/2-7.0));
        terminal_collar( (module_length/2-7.0));
    }
}

mcb_1p();
