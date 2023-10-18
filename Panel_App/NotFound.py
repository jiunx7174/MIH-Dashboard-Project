import panel as pn 

def NotFoundPanes():
    return pn.pane.HTML(
        '''<script src="https://unpkg.com/@dotlottie/player-component@latest/dist/dotlottie-player.mjs" type="module"></script> 

    <dotlottie-player src="https://lottie.host/1f5ce12a-da2d-4d4a-b619-69a407bd62e1/bIc0O3Q2vb.json" background="transparent" speed="0.5" style="width: 300px; height: 300px;" loop autoplay></dotlottie-player>'''
    )


