// ProjectOS / kicad-din-electrical
// Herstellerneutrale RCCB/RCD-Geometrie fuer 2P/4P-Prototypen.
// Alle Masse in mm. Keine Hersteller-CAD-Geometrie.

$fn = 48;

rcd_module_width = 18.0;
rcd_device_length = 84.0;
rcd_body_height = 62.0;
rcd_front_height = 12.0;
rcd_toggle_height = 6.0;

module rounded_box(size=[1,1,1], radius=1.0) {
    translate([-size[0]/2 + radius, -size[1]/2 + radius, radius])
        minkowski() {
            cube([size[0]-2*radius, size[1]-2*radius, size[2]-2*radius], center=false);
            sphere(r=radius);
        }
}

module rcd_body(poles=2) {
    width = poles * rcd_module_width;
    rounded_box([width, rcd_device_length, rcd_body_height], 1.0);
}

module rcd_front(poles=2) {
    width = poles * rcd_module_width - 4.0;
    translate([0, 0, rcd_body_height-0.5])
        rounded_box([width, 46.0, rcd_front_height], 0.8);
}

module rcd_toggle(poles=2) {
    width = max(12.0, poles * rcd_module_width - 14.0);
    translate([0, 4.0, rcd_body_height + rcd_front_height - 1.0])
        rotate([-10,0,0])
            rounded_box([width, 15.0, rcd_toggle_height], 0.8);
}

module rcd_test_button(poles=2) {
    x = -(poles * rcd_module_width)/2 + 8.0;
    translate([x, -13.0, rcd_body_height + rcd_front_height + 1.5])
        cylinder(h=3.0, d=7.0, center=true);
}

module rcd_terminal_collars(poles=2) {
    for (i=[0:poles-1]) {
        x = (i-(poles-1)/2) * rcd_module_width;
        for (sy=[-1,1]) {
            y = sy * (rcd_device_length/2 - 7.0);
            translate([x,y,rcd_body_height-2.0])
                difference() {
                    rounded_box([12.0,10.0,8.0],0.7);
                    translate([0,0,4.0]) cylinder(h=8.2,d=4.0,center=true);
                }
        }
    }
}

module rcd_device(poles=2) {
    union() {
        rcd_body(poles);
        rcd_front(poles);
        rcd_toggle(poles);
        rcd_test_button(poles);
        rcd_terminal_collars(poles);
    }
}
