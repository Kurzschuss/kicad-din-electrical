// ProjectOS / kicad-din-electrical
// Herstellerneutrales MCB-1P-Referenzmodell
// Von Grund auf neu erstellt; keine Hersteller-CAD-Geometrie übernommen.
// Alle Maße in mm.

$fn = 48;

// Projekt-Referenzmaße. Diese Geometrie ist kein Ersatz für konkrete Herstellerdaten.
module_width = 18.0;
body_height = 90.0;
body_depth = 70.0;

front_step_depth = 18.0;
front_step_height = 46.0;
front_step_z = 22.0;

terminal_width = 10.0;
terminal_height = 9.0;
terminal_depth = 8.0;
terminal_margin_z = 7.0;

toggle_width = 10.0;
toggle_height = 18.0;
toggle_depth = 8.0;
toggle_angle = -12;

rail_width = 35.0;
rail_height = 7.5;
rail_recess_depth = 7.0;
rail_center_z = 45.0;

// Koordinatensystem:
// X = Modulbreite, Y = Tiefe, Z = Höhe.
// Frontseite liegt bei Y = 0; Gerät wächst in +Y.

module rounded_box(size=[1,1,1], radius=1.0) {
    // Robuste vereinfachte Geometrie ohne externe Bibliotheken.
    minkowski() {
        cube([size[0]-2*radius, size[1]-2*radius, size[2]-2*radius], center=false);
        sphere(r=radius);
    }
}

module housing() {
    difference() {
        union() {
            translate([0, 0, 0])
                rounded_box([module_width, body_depth, body_height], 1.0);

            // Vorspringender Bedien-/Beschriftungsbereich an der Front.
            translate([1.5, -front_step_depth, front_step_z])
                rounded_box([module_width-3.0, front_step_depth+2.0, front_step_height], 0.8);
        }

        // Oberer und unterer neutraler Klemmenbereich.
        translate([(module_width-terminal_width)/2, -0.1, body_height-terminal_margin_z-terminal_height])
            cube([terminal_width, terminal_depth, terminal_height]);
        translate([(module_width-terminal_width)/2, -0.1, terminal_margin_z])
            cube([terminal_width, terminal_depth, terminal_height]);

        // Vereinfachte rückseitige Aufnahme für DIN-Schiene 35 x 7,5.
        translate([(module_width-rail_width)/2, body_depth-rail_recess_depth, rail_center_z-rail_height/2])
            cube([rail_width, rail_recess_depth+0.2, rail_height]);
    }
}

module toggle() {
    // Neutrales Betätigungselement ohne Herstellerform, Logo oder Beschriftung.
    translate([(module_width-toggle_width)/2, -front_step_depth-toggle_depth+1.0, 45.0])
        rotate([toggle_angle, 0, 0])
            rounded_box([toggle_width, toggle_depth, toggle_height], 0.8);
}

module terminal_collar(z0) {
    // Abstrakte Anschlusszone. Keine herstellerspezifische Schrauben-/Klemmengeometrie.
    translate([2.5, -4.0, z0])
        difference() {
            rounded_box([module_width-5.0, 6.0, 12.0], 0.7);
            translate([(module_width-5.0)/2-2.0, -0.2, 3.0])
                cube([4.0, 4.5, 6.0]);
        }
}

union() {
    housing();
    toggle();
    terminal_collar(4.0);
    terminal_collar(body_height-16.0);
}
