// ProjectOS / kicad-din-electrical
// Gemeinsame herstellerneutrale MCB-Geometrie für 1P/3P-Prototypen.
// Alle Maße in mm. Keine Hersteller-CAD-Geometrie.

$fn = 48;

mcb_module_width = 18.0;
mcb_module_length = 84.0;

// Prototypische Bauhöhe für den KiCad-Praxistest.
// Ziel: Gesamtmodell ca. 80 ... 85 mm hoch, damit die 3D-Darstellung
// proportional zur 104-mm-Testplatine bleibt.
mcb_body_height = 62.0;
mcb_front_step_width = 14.0;
mcb_front_step_length = 46.0;
mcb_front_step_height = 12.0;
mcb_toggle_width = 10.0;
mcb_toggle_length = 18.0;
mcb_toggle_height = 6.0;
mcb_toggle_angle = -12;

mcb_terminal_width = 10.0;
mcb_terminal_length = 12.0;
mcb_terminal_recess_depth = 8.0;

// KiCad-/PCB-Koordinatensystem:
// X = Modulraster, Y = Gerätelänge in Draufsicht, Z = Höhe über PCB.
// Ursprung = Mitte der gesamten Geräte-Draufsicht auf der PCB-Ebene.

module mcb_rounded_box_xy(size=[1,1,1], radius=1.0) {
    translate([-size[0]/2 + radius, -size[1]/2 + radius, radius])
        minkowski() {
            cube([size[0]-2*radius, size[1]-2*radius, size[2]-2*radius], center=false);
            sphere(r=radius);
        }
}

module mcb_housing() {
    difference() {
        mcb_rounded_box_xy([mcb_module_width, mcb_module_length, mcb_body_height], 1.0);
        for (sy = [-1, 1]) {
            translate([0, sy*(mcb_module_length/2-mcb_terminal_length/2), mcb_body_height-mcb_terminal_recess_depth/2])
                cube([mcb_terminal_width, mcb_terminal_length, mcb_terminal_recess_depth+0.2], center=true);
        }
    }
}

module mcb_front_step() {
    translate([0, 0, mcb_body_height-0.5])
        mcb_rounded_box_xy([mcb_front_step_width, mcb_front_step_length, mcb_front_step_height], 0.8);
}

module mcb_toggle() {
    translate([0, 0, mcb_body_height + mcb_front_step_height - 1.0])
        rotate([mcb_toggle_angle, 0, 0])
            mcb_rounded_box_xy([mcb_toggle_width, mcb_toggle_length, mcb_toggle_height], 0.8);
}

module mcb_terminal_collar(y0) {
    translate([0, y0, mcb_body_height-2.0])
        difference() {
            mcb_rounded_box_xy([mcb_module_width-5.0, 10.0, 8.0], 0.7);
            translate([0, 0, 4.0]) cylinder(h=8.2, d=4.0, center=true);
        }
}

module mcb_1p_at(x0=0) {
    translate([x0, 0, 0])
        union() {
            mcb_housing();
            mcb_front_step();
            mcb_toggle();
            mcb_terminal_collar(-(mcb_module_length/2-7.0));
            mcb_terminal_collar( (mcb_module_length/2-7.0));
        }
}

module mcb_poles(pole_count=1) {
    for (i = [0:pole_count-1]) {
        x0 = (i - (pole_count-1)/2) * mcb_module_width;
        mcb_1p_at(x0);
    }

    // Bei mehrpoligen Geräten verbindet ein neutraler Koppelsteg die Betätiger.
    if (pole_count > 1) {
        translate([0, 0, mcb_body_height + mcb_front_step_height + 2.0])
            mcb_rounded_box_xy([pole_count*mcb_module_width-6.0, 4.0, 3.0], 0.6);
    }
}
