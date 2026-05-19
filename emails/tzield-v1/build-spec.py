#!/usr/bin/env python3
"""Build the tzield-v1 email JSON spec."""
import json

BLACK = "#000000"
WHITE = "#FFFFFF"
BODY = "#414042"            # Template_Body_Black / Tzield/Dark Gray
LIGHT_BLUE = "#E4EEF7"      # Tzield/Light Blue
BRAND_BLUE = "#0023C8"      # Tzield/BrandColor
BUTTON_BLUE = "#80CBFF"     # Tzield/ButtonBlue
SUBHEADER = "#06537B"       # Text_SubHeader
CORAL = "#FF5000"           # Tzield/Coral
SCAFFOLD = "#FF00B7"        # Variable / scaffolding
NEUTRAL = "#F2F2F2"         # Neutral/Gray
BORDER_GREY = "#707070"
HIGHLIGHT_GREY = "#979797"
ASSET_LINK_GREY = "#414042"
FONT = "Arial, Helvetica, sans-serif"


def pad(t, r, b, l):
    return {"top": t, "right": r, "bottom": b, "left": l}


def link(href, alias):
    return {"href": href, "alias": alias}


# Image asset URLs captured from Figma during JSX extraction
SANOFI_LOGO_HEADER_DESKTOP = "https://www.figma.com/api/mcp/asset/8f9d8a5e-5216-45a6-984d-7f1d5662d965"
SANOFI_LOGO_HEADER_MOBILE = "https://www.figma.com/api/mcp/asset/d38b0fa1-41f4-4e4b-b8ec-70d0c8c37270"
TZIELD_LOGO_DESKTOP = "https://www.figma.com/api/mcp/asset/d1765a39-1fcf-44b7-9fb5-4e49f76f3b19"
TZIELD_LOGO_MOBILE = "https://www.figma.com/api/mcp/asset/5956d125-15db-4b6c-8a44-fd06091faddb"
HERO_DESKTOP = "https://www.figma.com/api/mcp/asset/6078d07c-8e70-4441-a7ae-136da5fc0375"
HERO_MOBILE = "https://www.figma.com/api/mcp/asset/508b575b-6707-49c7-a006-6792c7b9a790"
CHECK_RECTANGLE = "https://www.figma.com/api/mcp/asset/c5bd2d0d-7f55-45ba-a64c-319feb5f79f8"
CHECK_OVAL_1 = "https://www.figma.com/api/mcp/asset/85f1b494-df8f-4530-8538-24abdd56292b"
CHECK_OVAL_2 = "https://www.figma.com/api/mcp/asset/b495a4f7-fb3e-470d-984c-df50c8dbaea3"
SANOFI_LOGO_FOOTER_DESKTOP = "https://www.figma.com/api/mcp/asset/cbec2485-d6c6-46c0-a93c-9ea11cf0ba8b"
SANOFI_LOGO_FOOTER_MOBILE = "https://www.figma.com/api/mcp/asset/aae72c65-9331-471e-9e62-8a9cebaff283"


def s1_envelope():
    """Section 1 — Email envelope metadata (skip in production)."""
    return {
        "id": "section-1",
        "name": "Email Envelope Metadata",
        "figmaNodeId": "40000030:421",
        "skipInProduction": True,
        "padding": pad(12, 24, 12, 24),
        "nodes": [
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "alignment": "left",
                "content": [
                    {"text": "From: [Sanofi US <medintel@hcp-email.sanofi.us>]\nTo: [HCP email]\nDate: [MM/DD/YYYY> <HH:MM:AM/PM>]\nSubject: [Explore a[n] [new] indication for a T1D treatment option.]"}
                ],
            }
        ],
    }


def s2_preheader():
    return {
        "id": "section-2",
        "name": "Preheader",
        "figmaNodeId": "40000030:422",
        "skipInProduction": True,
        "background": LIGHT_BLUE,
        "padding": pad(12, 24, 12, 24),
        "nodes": [
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "alignment": "left",
                "content": [
                    {"text": "Preheader: ["},
                    {"text": "Learn about this treatment option for your patients."},
                    {"text": "]"},
                ],
            }
        ],
    }


def s3_nav():
    return {
        "id": "section-3",
        "name": "Top Nav Links",
        "figmaNodeId": "40000030:423",
        "background": LIGHT_BLUE,
        "padding": pad(12, 24, 12, 24),
        "nodes": [
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BRAND_BLUE,
                "alignment": "left",
                "content": [
                    {"text": "View in browser", "underline": True,
                     "link": link("#", "nav-view-in-browser")},
                    {"text": " "},
                    {"text": "|", "color": BODY},
                    {"text": " "},
                    {"text": "Contact a Rep", "underline": True,
                     "link": link("#", "nav-contact-a-rep")},
                    {"text": "|", "color": BODY},
                    {"text": " "},
                    {"text": "Unsubscribe", "underline": True,
                     "link": link("#", "nav-unsubscribe")},
                ],
            }
        ],
    }


def s4_header():
    """Section 4 — Header with logos, links, INDICATIONS, bullet list."""
    return {
        "id": "section-4",
        "name": "Header",
        "figmaNodeId": "40000030:424",
        "padding": pad(14, 0, 12, 0),
        "nodes": [
            # 1. Sanofi corporate logo, right-aligned, with bottom padding 14px and right padding 10px
            {
                "type": "image",
                "src": SANOFI_LOGO_HEADER_DESKTOP,
                "alt": "Sanofi",
                "width": 60,
                "height": 16,
                "decorative": False,
                "alignment": "right",
                "padding": pad(0, 10, 14, 0),
                "mobile": {
                    "src": SANOFI_LOGO_HEADER_MOBILE,
                    "width": 60,
                    "height": 16,
                    "preserveWidth": True,
                    "alignment": "right",
                    "padding": pad(0, 10, 14, 0),
                },
            },
            # 2. Coral separator bar (full-width 4px)
            {
                "type": "spacer",
                "height": 4,
                "background": CORAL,
            },
            # 3. Two-column row: Tzield logo + PI links (24px container padding, 50px gap inner)
            {
                "type": "multiColumn",
                "alignment": "left",
                "verticalAlignment": "center",
                "mobileLayout": "stack",
                "padding": pad(24, 24, 24, 24),
                "columns": [
                    {
                        "id": "tzield-logo-col",
                        "width": 214,
                        "alignment": "left",
                        "padding": pad(0, 0, 0, 0),
                        "content": {
                            "type": "image",
                            "src": TZIELD_LOGO_DESKTOP,
                            "alt": "TZIELD® (teplizumab-mzwv) Injection | 2mg/2mL",
                            "width": 214,
                            "height": 90,
                            "decorative": False,
                            "alignment": "left",
                            "padding": pad(0, 0, 0, 0),
                            "mobile": {
                                "src": TZIELD_LOGO_MOBILE,
                                "width": 214,
                                "height": 90,
                                "preserveWidth": True,
                                "alignment": "left",
                                "padding": pad(0, 0, 0, 0),
                            },
                        },
                        "mobile": {"preserveWidth": True, "hide": False, "alignment": "left"},
                    },
                    {
                        "id": "pi-links-col",
                        "width": 201,
                        "borderLeft": {"width": 1, "color": BRAND_BLUE, "hideOnMobile": True},
                        "alignment": "left",
                        "padding": pad(0, 0, 0, 24),
                        "content": {
                            "type": "textBlock",
                            "fontFamily": FONT,
                            "fontSize": 16,
                            "lineHeight": 18,
                            "color": BRAND_BLUE,
                            "alignment": "left",
                            "content": [
                                {"text": "Read Indication and\nFull Prescribing Information",
                                 "underline": True,
                                 "link": link("#", "header-read-indication-pi")},
                                {"text": "\n\n"},
                                {"text": "Full Prescribing Information",
                                 "underline": True,
                                 "link": link("#", "header-pi-link")},
                                {"text": ", "},
                                {"text": "including boxed WARNING",
                                 "underline": True,
                                 "link": link("#", "header-boxed-warning")},
                            ],
                        },
                        "mobile": {"preserveWidth": True, "hide": False, "alignment": "left"},
                    },
                ],
                "gaps": [
                    {"between": ["tzield-logo-col", "pi-links-col"],
                     "desktop": 50, "mobile": 50, "direction": "auto"}
                ],
            },
            # 4. INDICATIONS heading
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 19,
                "lineHeight": 23,
                "fontWeight": "bold",
                "color": BRAND_BLUE,
                "alignment": "left",
                "padding": pad(0, 24, 24, 24),
                "content": [{"text": "INDICATIONS"}],
            },
            # 5. Indication intro text
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "alignment": "left",
                "padding": pad(0, 24, 0, 24),
                "content": [
                    {"text": "TZIELD is a disease-modifying agent that preserves beta-cell function indicated:"}
                ],
            },
            # 6. Bullet list of indications
            {
                "type": "list",
                "style": "bullet",
                "indent": 24,
                "bulletColor": BODY,
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "itemSpacing": 0,
                "padding": pad(0, 24, 0, 24),
                "items": [
                    {"content": [
                        {"text": "to delay the onset of Stage 3 type 1 diabetes (T1D) in adults and pediatric patients aged 8 years and older with Stage 2 T1D."}
                    ]},
                    {"content": [
                        {"text": "to delay the progression of Stage 3 T1D in adults and pediatric patients 8 years and older recently diagnosed with Stage 3 T1D. This indication is approved under accelerated approval based on C-peptide as a marker of beta-cell preservation. Continued approval for this indication may be contingent upon verification and description of clinical benefit in confirmatory trials."}
                    ]},
                ],
            },
        ],
    }


def s5_new_indication_banner():
    return {
        "id": "section-5",
        "name": "NEW INDICATION Banner",
        "figmaNodeId": "40000030:425",
        "background": SUBHEADER,
        "padding": pad(12, 24, 12, 24),
        "nodes": [
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 30,
                "lineHeight": 34,
                "fontWeight": "bold",
                "color": LIGHT_BLUE,
                "alignment": "left",
                "content": [
                    {"text": "["},
                    {"text": "NEW INDICATION"},
                    {"text": "]"},
                    {"text": " FOR APPROPRIATE PATIENTS"},
                    {"text": "1", "fontSize": 19, "superscript": True},
                ],
            }
        ],
    }


def s6_approval_announcement():
    return {
        "id": "section-6",
        "name": "Approval Announcement",
        "figmaNodeId": "40000030:426",
        "background": BRAND_BLUE,
        "padding": pad(12, 24, 12, 24),
        "nodes": [
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 19,
                "lineHeight": 23,
                "color": WHITE,
                "alignment": "left",
                "content": [
                    {"text": "Due to the significant unmet need in T1D and years of clinical research, TZIELD has been approved for patients with Stage 3 T1D within "},
                    {"text": "["},
                    {"text": "6-12 weeks"},
                    {"text": "] "},
                    {"text": "of diagnosis as the first therapy under the FDA’s Commissioner National Priority Voucher (CNPV) program."},
                    {"text": "2", "fontSize": 12, "superscript": True},
                ],
            }
        ],
    }


def s7_hero():
    return {
        "id": "section-7",
        "name": "Hero Image",
        "figmaNodeId": "40000030:427",
        "padding": pad(12, 0, 12, 0),
        "nodes": [
            {
                "type": "image",
                "src": HERO_DESKTOP,
                "alt": "",
                "decorative": True,
                "width": 600,
                "height": 300,
                "alignment": "center",
                "padding": pad(0, 0, 0, 0),
                "mobile": {
                    "src": HERO_MOBILE,
                    "width": 360,
                    "height": 288,
                    "preserveWidth": False,
                    "alignment": "center",
                    "padding": pad(0, 0, 0, 0),
                },
            }
        ],
    }


def s8_stages_continuum():
    """Heading + 2 checkmark rows."""
    def checkmark_row(text_content, col_id_prefix):
        return {
            "type": "multiColumn",
            "alignment": "left",
            "verticalAlignment": "center",
            "mobileLayout": "stack",
            "padding": pad(0, 24, 0, 24),
            "columns": [
                {
                    "id": f"{col_id_prefix}-icon",
                    "width": 110,
                    "alignment": "center",
                    "padding": pad(0, 0, 0, 0),
                    "content": {
                        "type": "image",
                        "src": CHECK_OVAL_1,
                        "alt": "",
                        "decorative": True,
                        "width": 110,
                        "height": 110,
                        "alignment": "center",
                        "padding": pad(0, 0, 0, 0),
                        "mobile": {
                            "src": CHECK_OVAL_1,
                            "width": 110,
                            "height": 110,
                            "preserveWidth": True,
                            "alignment": "center",
                            "padding": pad(0, 0, 0, 0),
                        },
                    },
                    "mobile": {"preserveWidth": True, "hide": False, "alignment": "center"},
                },
                {
                    "id": f"{col_id_prefix}-text",
                    "width": 394,
                    "alignment": "left",
                    "padding": pad(0, 0, 0, 24),
                    "content": {
                        "type": "textBlock",
                        "fontFamily": FONT,
                        "fontSize": 20,
                        "lineHeight": 28,
                        "fontWeight": "bold",
                        "color": BODY,
                        "alignment": "left",
                        "content": text_content,
                    },
                    "mobile": {"preserveWidth": False, "hide": False, "alignment": "center"},
                },
            ],
            "gaps": [
                {"between": [f"{col_id_prefix}-icon", f"{col_id_prefix}-text"],
                 "desktop": 0, "mobile": 24, "direction": "auto"}
            ],
        }

    return {
        "id": "section-8",
        "name": "Stages Continuum + Checkmarks",
        "figmaNodeId": "40000030:428",
        "padding": pad(12, 0, 12, 0),
        "nodes": [
            # Heading
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 30,
                "lineHeight": 34,
                "fontWeight": "bold",
                "color": BRAND_BLUE,
                "alignment": "left",
                "padding": pad(0, 24, 0, 24),
                "content": [
                    {"text": "TZIELD has expanded across the following stages of the T1D disease continuum"},
                    {"text": "1", "fontSize": 19, "superscript": True},
                ],
            },
            # Row 1
            checkmark_row(
                [{"text": "APPROVED in Stage 2 T1D"}],
                "stage-2"
            ),
            # Row 2
            checkmark_row(
                [
                    {"text": "["},
                    {"text": "NOW"},
                    {"text": "]"},
                    {"text": " APPROVED in Stage 3 T1D within "},
                    {"text": "["},
                    {"text": "6-12 weeks"},
                    {"text": "]"},
                    {"text": " of diagnosis"},
                ],
                "stage-3"
            ),
        ],
    }


def s9_abbreviation():
    return {
        "id": "section-9",
        "name": "Abbreviation Footnote",
        "figmaNodeId": "40000030:429",
        "padding": pad(12, 24, 12, 24),
        "nodes": [
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 19,
                "lineHeight": 23,
                "color": BODY,
                "alignment": "left",
                "content": [{"text": "T1D=type 1 diabetes."}],
            }
        ],
    }


def s10_cta():
    return {
        "id": "section-10",
        "name": "Learn More + Discover Button",
        "figmaNodeId": "40000030:430",
        "background": LIGHT_BLUE,
        "padding": pad(12, 24, 12, 24),
        "nodes": [
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 19,
                "lineHeight": 23,
                "color": BLACK,
                "alignment": "center",
                "padding": pad(0, 0, 24, 0),
                "content": [
                    {"text": "Learn more about the"},
                    {"text": " ["},
                    {"text": "new"},
                    {"text": "] "},
                    {"text": "indication"},
                ],
            },
            {
                "type": "button",
                "label": "Discover More",
                "link": link("#", "cta-discover-more"),
                "background": BRAND_BLUE,
                "textColor": WHITE,
                "border": {"width": 4, "color": BUTTON_BLUE},
                "borderRadius": 0,
                "width": 444,
                "height": 88,
                "fontFamily": FONT,
                "fontSize": 20,
                "lineHeight": 24,
                "fontWeight": "bold",
                "alignment": "center",
                "padding": pad(0, 0, 0, 0),
                "mobile": {
                    "width": 204,
                    "height": 98,
                    "fluid": False,
                },
            },
        ],
    }


def s11_isi():
    return {
        "id": "section-11",
        "name": "Important Safety Information",
        "figmaNodeId": "40000030:431",
        "padding": pad(12, 24, 12, 24),
        "nodes": [
            # 1. ISI heading
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 19,
                "lineHeight": 23,
                "fontWeight": "bold",
                "color": BRAND_BLUE,
                "alignment": "left",
                "padding": pad(0, 0, 24, 0),
                "content": [{"text": "IMPORTANT SAFETY INFORMATION"}],
            },
            # 2. WARNINGS AND PRECAUTIONS
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "fontWeight": "bold",
                "color": BODY,
                "alignment": "left",
                "padding": pad(0, 0, 24, 0),
                "content": [{"text": "WARNINGS AND PRECAUTIONS"}],
            },
            # 3. Warnings bullet list
            {
                "type": "list",
                "style": "bullet",
                "indent": 24,
                "bulletColor": BODY,
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "itemSpacing": 0,
                "padding": pad(0, 0, 24, 0),
                "items": [
                    {"content": [
                        {"text": "Cytokine Release Syndrome (CRS):", "bold": True},
                        {"text": " CRS occurred in TZIELD-treated patients during the treatment period and through 28 days after the last drug administration. Prior to TZIELD treatment, premedicate with antipyretics, antihistamines and/or antiemetics, and treat similarly if symptoms occur during treatment. If severe CRS develops, consider pausing dosing for 1 day to 2 days and administering the remaining doses to complete the full 14-day course on consecutive days; or discontinue treatment. Monitor liver enzymes and bilirubin during treatment. Discontinue TZIELD treatment in patients who develop elevated alanine aminotransferase or aspartate aminotransferase more than 5 times the upper limit of normal (ULN) or bilirubin more than 3 times ULN."}
                    ]},
                    {"content": [
                        {"text": "Serious Infections:", "bold": True},
                        {"text": " Use of TZIELD is not recommended in patients with active serious infection or chronic infection other than localized skin infections. Monitor patients for signs and symptoms of infection during and after TZIELD administration. If serious infection develops, treat appropriately, and discontinue TZIELD."}
                    ]},
                    {"content": [
                        {"text": "Lymphopenia: ", "bold": True},
                        {"text": "Lymphopenia occurred in most TZIELD-treated patients. For most patients, lymphocyte levels began to recover after the fifth day of treatment and returned to pretreatment values within two weeks after treatment completion and without dose interruption. Monitor white blood cell counts during the treatment period. If prolonged severe lymphopenia develops (<500 cells per mcL lasting 1 week or longer), discontinue TZIELD."}
                    ]},
                    {"content": [
                        {"text": "Hypersensitivity Reactions:", "bold": True},
                        {"text": " Acute hypersensitivity reactions including serum sickness, angioedema, urticaria, rash, vomiting and bronchospasm occurred in TZIELD-treated patients. If severe hypersensitivity reactions occur, discontinue TZIELD and treat promptly."}
                    ]},
                    {"content": [
                        {"text": "Vaccinations: ", "bold": True},
                        {"text": "The safety of immunization with live-attenuated (live) vaccines with TZIELD-treated patients has not been studied. TZIELD may interfere with immune response to vaccination and decrease vaccine efficacy. Administer all age-appropriate vaccinations prior to starting TZIELD.\n- Administer live vaccines at least 8 weeks prior to treatment. Live vaccines are not recommended during treatment, or up to 52 weeks after treatment.\n- Administer inactivated (killed) vaccines or mRNA vaccines at least 2 weeks prior to treatment. Inactivated vaccines are not recommended within 2 weeks prior to any TZIELD treatment course, during treatment, or 6 weeks after completion of treatment."}
                    ]},
                    {"content": [
                        {"text": "Glucose Monitoring in Patients Recently Diagnosed with Stage 3 T1D: ", "bold": True},
                        {"text": "Patients using insulin should be monitored according to current practice guidelines."}
                    ]},
                ],
            },
            # 4. ADVERSE REACTIONS heading
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "fontWeight": "bold",
                "color": BODY,
                "alignment": "left",
                "padding": pad(0, 0, 24, 0),
                "content": [{"text": "ADVERSE REACTIONS"}],
            },
            # 5. ADVERSE REACTIONS body
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "alignment": "left",
                "padding": pad(0, 0, 24, 0),
                "content": [{"text": "Most common adverse reactions (>10%) were lymphopenia, rash, leukopenia, neutropenia, increased liver transaminase, and headache."}],
            },
            # 6. USE IN SPECIFIC POPULATIONS heading
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "fontWeight": "bold",
                "color": BODY,
                "alignment": "left",
                "padding": pad(0, 0, 24, 0),
                "content": [{"text": "USE IN SPECIFIC POPULATIONS"}],
            },
            # 7. Populations bullet list
            {
                "type": "list",
                "style": "bullet",
                "indent": 24,
                "bulletColor": BODY,
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "itemSpacing": 0,
                "padding": pad(0, 0, 24, 0),
                "items": [
                    {"content": [
                        {"text": "Pregnancy:", "bold": True},
                        {"text": " May cause fetal harm."}
                    ]},
                    {"content": [
                        {"text": "Lactation:", "bold": True},
                        {"text": " A lactating woman may consider pumping and discarding breast milk during and for 20 days after TZIELD administration."}
                    ]},
                ],
            },
            # 8. Prescribing Information paragraph
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "alignment": "left",
                "padding": pad(0, 0, 24, 0),
                "content": [
                    {"text": "Please see full "},
                    {"text": "Prescribing Information",
                     "color": BRAND_BLUE, "underline": True,
                     "link": link("#", "isi-prescribing-info")},
                    {"text": ", including patient selection criteria."},
                ],
            },
            # 9. Counterfeit drugs paragraph
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "alignment": "left",
                "content": [
                    {"text": "Click here",
                     "color": BRAND_BLUE, "underline": True,
                     "link": link("#", "isi-counterfeit")},
                    {"text": " to learn more about Sanofi’s commitment to fighting counterfeit drugs."},
                ],
            },
        ],
    }


def s12_references():
    return {
        "id": "section-12",
        "name": "References",
        "figmaNodeId": "40000030:432",
        "padding": pad(12, 24, 12, 24),
        "nodes": [
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "fontWeight": "bold",
                "color": BODY,
                "alignment": "left",
                "padding": pad(0, 0, 24, 0),
                "content": [{"text": "References:"}],
            },
            {
                "type": "list",
                "style": "numbered",
                "indent": 24,
                "bulletColor": BODY,
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "itemSpacing": 12,
                "padding": pad(0, 0, 0, 0),
                "items": [
                    {"content": [
                        {"text": "TZIELD Prescribing Information. Provention Bio, Inc; "},
                        {"text": "["},
                        {"text": "2025."},
                        {"text": "]"},
                    ]},
                    {"content": [
                        {"text": "["},
                        {"text": "Press release pending"},
                        {"text": "]"},
                    ]},
                ],
            },
        ],
    }


def s13_survey():
    """Survey/CXQ — intermediate container pattern with rating scale."""
    def rating_box(num, highlighted=False):
        bg = HIGHLIGHT_GREY if highlighted else WHITE
        border_color = HIGHLIGHT_GREY if highlighted else BORDER_GREY
        text_color = WHITE if highlighted else BLACK
        return {
            "id": f"cxq-rating-{num}",
            "width": 72,
            "height": 48,
            "background": bg,
            "border": {"top": 1, "right": 1, "bottom": 1, "left": 1, "color": border_color},
            "link": link("#", f"cxq-rating-{num}"),
            "alignment": "center",
            "padding": pad(0, 0, 0, 0),
            "content": {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 48,
                "fontWeight": "bold",
                "color": text_color,
                "alignment": "center",
                "content": [{"text": str(num)}],
                "mobile": {"lineHeight": 40, "fontSize": 16, "alignment": "center"},
            },
            "mobile": {"width": 40, "height": 40, "preserveWidth": False},
        }

    return {
        "id": "section-13",
        "name": "Survey CXQ",
        "figmaNodeId": "40000030:433",
        "outerPadding": pad(12, 0, 12, 0),
        "padding": pad(24, 24, 24, 24),
        "background": NEUTRAL,
        "nodes": [
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BODY,
                "alignment": "center",
                "padding": pad(0, 0, 10, 0),
                "content": [{"text": "Your feedback is important to us. To help us improve our offering, you are invited to respond to the question below and complete a short survey."}],
            },
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 19,
                "lineHeight": 22,
                "fontWeight": "bold",
                "color": BLACK,
                "alignment": "center",
                "padding": pad(0, 0, 10, 0),
                "content": [{"text": "How relevant is the content of this email to you?"}],
            },
            # Labels row
            {
                "type": "multiColumn",
                "alignment": "left",
                "mobileLayout": "preserve",
                "padding": pad(0, 0, 10, 0),
                "columns": [
                    {
                        "id": "cxq-label-not",
                        "width": "50%",
                        "alignment": "left",
                        "padding": pad(0, 0, 0, 0),
                        "content": {
                            "type": "textBlock",
                            "fontFamily": FONT,
                            "fontSize": 19,
                            "lineHeight": 22,
                            "fontWeight": "bold",
                            "color": BLACK,
                            "alignment": "left",
                            "content": [{"text": "Not relevant"}],
                        },
                        "mobile": {"preserveWidth": True, "hide": False, "alignment": "left"},
                    },
                    {
                        "id": "cxq-label-very",
                        "width": "50%",
                        "alignment": "right",
                        "padding": pad(0, 0, 0, 0),
                        "content": {
                            "type": "textBlock",
                            "fontFamily": FONT,
                            "fontSize": 19,
                            "lineHeight": 22,
                            "fontWeight": "bold",
                            "color": BLACK,
                            "alignment": "right",
                            "content": [{"text": "Very relevant"}],
                        },
                        "mobile": {"preserveWidth": True, "hide": False, "alignment": "right"},
                    },
                ],
                "gaps": [
                    {"between": ["cxq-label-not", "cxq-label-very"],
                     "desktop": 0, "mobile": 0, "direction": "auto"}
                ],
            },
            # Rating boxes
            {
                "type": "multiColumn",
                "alignment": "left",
                "mobileLayout": "preserve",
                "padding": pad(0, 0, 0, 0),
                "columns": [rating_box(n, highlighted=(n == 2)) for n in range(1, 8)],
                "gaps": [
                    {"between": [f"cxq-rating-{n}", f"cxq-rating-{n+1}"],
                     "desktop": 8, "mobile": 5, "direction": "auto"}
                    for n in range(1, 7)
                ],
            },
        ],
    }


def s14_footer():
    return {
        "id": "section-14",
        "name": "Footer",
        "figmaNodeId": "40000030:434",
        "padding": pad(12, 24, 12, 24),
        "nodes": [
            # 1. State price disclosure
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 21,
                "color": BLACK,
                "alignment": "left",
                "content": [
                    {"text": "Prescribers and other Healthcare Professionals may "},
                    {"text": "click here",
                     "color": BRAND_BLUE, "underline": True,
                     "link": link("#", "footer-state-price")},
                    {"text": " for State Price Disclosure Information."},
                ],
            },
            # 2. Do not reply
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 21,
                "color": BLACK,
                "alignment": "left",
                "padding": pad(16, 0, 0, 0),
                "content": [
                    {"text": "Please do not reply to this message.", "bold": True},
                    {"text": " Sanofi US will not receive a message if you reply."},
                ],
            },
            # 3. Sanofi logo
            {
                "type": "image",
                "src": SANOFI_LOGO_FOOTER_DESKTOP,
                "alt": "Sanofi",
                "width": 88,
                "height": 24,
                "decorative": False,
                "alignment": "left",
                "padding": pad(16, 24, 14, 0),
                "mobile": {
                    "src": SANOFI_LOGO_FOOTER_MOBILE,
                    "width": 88,
                    "height": 24,
                    "preserveWidth": True,
                    "alignment": "left",
                    "padding": pad(16, 24, 14, 0),
                },
            },
            # 4. Address block
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BLACK,
                "alignment": "left",
                "padding": pad(0, 0, 16, 0),
                "content": [
                    {"text": "Sanofi US\n100 Morris Street,\nMorristown, NJ 07960"}
                ],
            },
            # 5. Copyright + links block
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BLACK,
                "alignment": "left",
                "content": [
                    {"text": "© 2026 Sanofi. All rights reserved.\n\n"},
                    {"text": "Legal Disclaimer",
                     "color": BRAND_BLUE, "underline": True,
                     "link": link("#", "footer-legal-disclaimer")},
                    {"text": " and "},
                    {"text": "Privacy Policy",
                     "color": BRAND_BLUE, "underline": True,
                     "link": link("#", "footer-privacy-policy")},
                    {"text": "\n\nQuestions and Comments? "},
                    {"text": "Click here",
                     "color": BRAND_BLUE, "underline": True,
                     "link": link("#", "footer-questions-comments")},
                    {"text": " to contact us.\n\nThis email is intended for use by US residents only.\n\nYou may unsubscribe from Sanofi by "},
                    {"text": "clicking here",
                     "color": BRAND_BLUE, "underline": True,
                     "link": link("#", "footer-unsubscribe")},
                    {"text": " or calling 1-800-633-1610."},
                ],
            },
            # 6. MAT job code (was SCAFFOLD pink in Figma — recolored to body BLACK)
            {
                "type": "textBlock",
                "fontFamily": FONT,
                "fontSize": 16,
                "lineHeight": 20,
                "color": BLACK,
                "alignment": "left",
                "padding": pad(16, 0, 0, 0),
                "content": [{"text": "MAT-US-2510989-v1.0-10/2025"}],
            },
        ],
    }


sections = [
    s1_envelope(),
    s2_preheader(),
    s3_nav(),
    s4_header(),
    s5_new_indication_banner(),
    s6_approval_announcement(),
    s7_hero(),
    s8_stages_continuum(),
    s9_abbreviation(),
    s10_cta(),
    s11_isi(),
    s12_references(),
    s13_survey(),
    s14_footer(),
]

spec = {
    "specVersion": "2.0.0",
    "meta": {
        "emailName": "tzield-now-approved-day1-crm",
        "figmaFile": "uVU9ZnWB6iZO0kgY4bztS9",
        "subjectLine": "Explore a[n] [new] indication for a T1D treatment option.",
        "previewText": "Learn about this treatment option for your patients.",
        "desktopWidth": 600,
        "mobileWidth": 360,
        "openQuestions": [
            {"id": "hero-decorative-bars-overlay",
             "question": "The right edge of the hero (section-7) has decorative vertical bars (coral 8px + blue 16px) overlaying the photo in Figma (canvas-level sibling node 40000030:438 / 40000030:458). Email HTML cannot render this as an overlay. Bake the decorative bars into the exported hero image asset before launch so the photo + bars ship as one image.",
             "blocking": True},
            {"id": "section-13-bracket-overlay",
             "question": "The survey/CXQ section (section-13) has a decorative bracket frame [ ] (canvas-level sibling node 40000030:435 / 40000030:454) overlaying its left and right edges in Figma. Decide whether to bake the decorative brackets into the rendered survey container or omit them from production HTML.",
             "blocking": True},
            {"id": "hero-alt-text",
             "question": "Provide alt text for the hero image (section-7) or confirm it's decorative. Current spec marks decorative:true since it's a brand lifestyle image with no informational content.",
             "blocking": False},
            {"id": "section-8-checkmark-alt",
             "question": "Confirm the orange checkmark icons in section-8 are decorative (paired with adjacent text). Current spec marks decorative:true.",
             "blocking": False},
        ],
    },
    "annotations": {
        "stripBrackets": True,
        "stripColors": ["#FF00B7"],
        "recolorMap": {},
    },
    "sections": sections,
}

out_path = "/home/user/design-to-code/emails/tzield-v1/tzield-v1-spec.json"
with open(out_path, "w") as f:
    json.dump(spec, f, indent=2)

print(f"Wrote {out_path}")
print(f"Sections: {len(sections)}")
print(f"Open questions: {len(spec['meta']['openQuestions'])}")
