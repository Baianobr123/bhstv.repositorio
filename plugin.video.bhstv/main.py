# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcplugin
import urllib.request
import urllib.parse
import re

URLS = {
    'canais': "https://gitlab.com/BHS_TV/bhs_tv/-/raw/main/CHANNELS.txt?ref_type=heads",
    'filmes': "https://gitlab.com/BHS_TV/bhs_tv/-/raw/main/MOVIES.txt?ref_type=heads",
    'series': "https://gitlab.com/BHS_TV/bhs_tv/-/raw/main/SERIES.txt?ref_type=heads"
}
IMG_SEARCH = "https://i.imgur.com/xeUbPyj.png"
IMG_TV = "https://i.imgur.com/31vnSVm.png"
IMG_MOVIES = "https://i.imgur.com/1gWW9MP.png"
IMG_SERIES = "https://i.imgur.com/hsVp6Rr.png"
FANART = "https://i.imgur.com/uuRf2gE.jpg"
HANDLE = int(sys.argv[1])
U_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'

def get_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': U_AGENT})
        with urllib.request.urlopen(req, timeout=20) as response:
            data = response.read().decode('utf-8', 'ignore')
            xbmc.log(f"[BHS TV] Dados baixados com sucesso: {url[:50]}... ({len(data)} chars)", xbmc.LOGINFO)
            return data
    except Exception as e:
        xbmc.log(f"[BHS TV] Erro ao baixar {url}: {str(e)}", xbmc.LOGERROR)
        return ""

def add_dir(name, url, icon, folder=True):
    li = xbmcgui.ListItem(label=name)
    li.setArt({'thumb': icon, 'icon': icon, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(HANDLE, url, li, folder)

def parse_block(block):
    try:
        block = block.strip()
        if not block: return None, None, None
        nome = block.split(',')[-1].strip()
        logo_match = re.search(r'tvg-logo="(.*?)"', block)
        img = logo_match.group(1) if logo_match else None
        link_matches = re.findall(r'(http[s]?://[^\s"\'<>]+)', block)
        link = link_matches[-1].strip() if link_matches else None
        if not link:
            return None, None, None
        return nome, link, img
    except Exception as e:
        xbmc.log(f"[BHS TV] Erro no parse_block: {str(e)} | Block: {block[:200]}", xbmc.LOGERROR)
        return None, None, None

def main():
    param = sys.argv[2] if len(sys.argv) > 2 else ""
   
    if not param or param == "":
        xbmcgui.Dialog().ok('[COLOR FF87CEEB]BHS TV[/COLOR]', '[B] [COLOR white]Seja bem-vindo ao seu sistema de entretenimento![/COLOR] [/B]\n[B][COLOR green]Sua conta está ativa e pronta para uso.[/COLOR][/B]')
        add_dir('[B] [COLOR silver]🔍BHS TV - PESQUISAR[/COLOR] [/B]', sys.argv[0] + '?mode=search', IMG_SEARCH)
        add_dir('📺 [B] [COLOR white]BHS[/COLOR] [COLOR red]TV[/COLOR] [COLOR white]-[/COLOR] [COLOR white]TV A[/COLOR][COLOR red]O VIVO[/COLOR] [/B]', sys.argv[0] + '?mode=list_cats&type=canais', IMG_TV)
        add_dir('🎬 [B] [COLOR white]BHS[/COLOR] [COLOR red]TV[/COLOR] [COLOR white]-[/COLOR] [COLOR white]FIL[/COLOR][COLOR red]MES[/COLOR] [/B]', sys.argv[0] + '?mode=list_cats&type=filmes', IMG_MOVIES)
        add_dir('🍿 [B] [COLOR white]BHS[/COLOR] [COLOR red]TV[/COLOR] [COLOR white]-[/COLOR] [COLOR white]SÉRIES[/COLOR] [COLOR lime]/[/COLOR] [COLOR red]ANIMES[/COLOR] [/B]', sys.argv[0] + '?mode=list_cats&type=series', IMG_SERIES)
   
    elif 'mode=list_cats' in param:
        t = 'canais' if 'type=canais' in param else ('series' if 'type=series' in param else 'filmes')
        data = get_data(URLS[t])
        if not data:
            xbmcgui.Dialog().ok("Erro", "Não foi possível carregar as categorias.")
            return
        cats = sorted(list(set(re.findall(r'group-title="(.*?)"', data))))
        if not cats:
            xbmc.log("[BHS TV] Nenhuma categoria encontrada", xbmc.LOGWARNING)
        for c in cats:
            url = sys.argv[0] + '?mode=list_items&type=' + t + '&cat=' + urllib.parse.quote_plus(c)
            icon = IMG_TV if t == 'canais' else (IMG_MOVIES if t == 'filmes' else IMG_SERIES)
            add_dir(c, url, icon)
   
    elif 'mode=search' in param:
        text = xbmcgui.Dialog().input('Pesquisar')
        if not text:
            return
        text = text.lower()
        for t in ['canais', 'filmes', 'series']:
            data = get_data(URLS[t])
            if not data: continue
            blocos = re.split(r'#EXTINF:', data, flags=re.IGNORECASE)[1:]
            for b in blocos:
                full_block = '#EXTINF:' + b
                if text in full_block.lower():
                    nome, link, img = parse_block(full_block)
                    if not nome or not link: continue
                    icon = img or (IMG_TV if t == 'canais' else (IMG_MOVIES if t == 'filmes' else IMG_SERIES))
                    li = xbmcgui.ListItem(label=nome)
                    li.setLabel2('')  # <-- OCULTA A URL AQUI
                    li.setArt({'thumb': icon, 'icon': icon, 'fanart': FANART})
                    li.setInfo('video', {'title': nome})
                    li.setProperty('IsPlayable', 'true')
                    full_path = link + '|User-Agent=' + urllib.parse.quote(U_AGENT)
                    if link.endswith('.m3u8'):
                        li.setProperty('inputstream', 'inputstream.adaptive')
                        li.setProperty('inputstream.adaptive.manifest_type', 'hls')
                        li.setMimeType('application/vnd.apple.mpegurl')
                        li.setContentLookup(False)
                    xbmcplugin.addDirectoryItem(HANDLE, full_path, li, False)
   
    elif 'mode=list_items' in param:
        t = 'canais' if 'type=canais' in param else ('series' if 'type=series' in param else 'filmes')
        query = urllib.parse.parse_qs(param[1:])
        cat_target = urllib.parse.unquote_plus(query.get('cat', [''])[0])
        data = get_data(URLS[t])
        if not data:
            xbmcgui.Dialog().ok("Erro", "Não foi possível carregar os itens.")
            return
        blocos = re.split(r'#EXTINF:', data, flags=re.IGNORECASE)[1:]
        count = 0
        for b in blocos:
            full_block = '#EXTINF:' + b
            if f'group-title="{cat_target}"' in full_block or cat_target in full_block:
                nome, link, img = parse_block(full_block)
                if not nome or not link: continue
                icon = img or (IMG_TV if t == 'canais' else (IMG_MOVIES if t == 'filmes' else IMG_SERIES))
                li = xbmcgui.ListItem(label=nome)
                li.setLabel2('')  # <-- OCULTA A URL AQUI
                li.setArt({'thumb': icon, 'icon': icon, 'fanart': FANART})
                li.setInfo('video', {'title': nome})
                li.setProperty('IsPlayable', 'true')
                full_path = link + '|User-Agent=' + urllib.parse.quote(U_AGENT)
                if link.endswith('.m3u8') or link.endswith('.mp4'):
                    if link.endswith('.m3u8'):
                        li.setProperty('inputstream', 'inputstream.adaptive')
                        li.setProperty('inputstream.adaptive.manifest_type', 'hls')
                        li.setMimeType('application/vnd.apple.mpegurl')
                        li.setContentLookup(False)
                xbmcplugin.addDirectoryItem(HANDLE, full_path, li, False)
                count += 1
        xbmc.log(f"[BHS TV] Adicionados {count} itens para categoria {cat_target}", xbmc.LOGINFO)
   
    xbmcplugin.endOfDirectory(HANDLE)

if __name__ == '__main__':
    main()