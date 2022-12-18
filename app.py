import dash
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, dcc, html

KISR_LOGO = 'assets/imgs/background.png'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY],
                assets_folder='assets/', use_pages=True)


def create_nav_item(name, path, href):
    return dbc.NavItem(dbc.NavLink(f"{name} - {path}", href=href))


def create_links():
    return dbc.Row(
        class_name="ms-auto",
        style=dict(border='1px solid yellow', height='100%'),
        children=[
            dbc.Col(
                style=dict(height='100%'),
                children=[
                    dbc.NavItem(
                        style=dict(height='100%'),
                        children=[
                            dbc.NavLink(
                                href=f"{page['relative_path']}",
                                style=dict(
                                    border='1px solid red',
                                    height='100%'
                                ),
                                children=f"{page['name']}",
                            ),
                        ]
                    )
                ],
            )
            for page in dash.page_registry.values()
        ],
    )


app.layout = dbc.Container(
    style=dict(
        backgroundImage='url(assets/imgs/background.png)',
        backgroundSize='100% 100%',
        height='100%',
        width='100%',
    ),
    fluid=True,
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dbc.Navbar(
                            color='dark',
                            sticky='top',
                            expand='xl',
                            children=[
                                dbc.Row(
                                    children=[
                                        dbc.Col(
                                            html.A(
                                                html.Img(
                                                    src='assets/imgs/logo.png',
                                                    height='60px'),
                                                href='https://www.kisr.edu.kw/en/'
                                            )
                                        )
                                    ]
                                ),
                                dbc.NavbarToggler(
                                    id="navbar-toggler",
                                    n_clicks=0
                                ),
                                dbc.Collapse(
                                    id="navbar-collapse",
                                    is_open=False,
                                    navbar=True,
                                    children=[
                                        dbc.NavItem(
                                            dbc.NavLink('Live Feed', href='/')
                                        ),
                                        dbc.NavItem(
                                            dbc.NavLink(
                                                'Historical Data',
                                                href='/historical'
                                            )
                                        ),
                                    ],
                                )
                            ],
                        ),
                        dash.page_container
                    ]
                )
            ]
        )
    ]
)


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(port=3001, debug=True)
