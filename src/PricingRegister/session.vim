let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/Desktop/zmp/side-work/client-project-scraper
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
let s:shortmess_save = &shortmess
if &shortmess =~ 'A'
  set shortmess=aoOA
else
  set shortmess=aoO
endif
badd +28 src/readme.md
badd +20 src/PricingRegister/lib/ssm_manager.py
badd +21 src/PricingRegister/lib/sns_manager.py
badd +1 src/PricingRegister/registers/printpac_multi_sticker_reg.py
badd +17 src/PricingRegister/global_settings.py
badd +39 src/PricingRegister/lib/bq_manager.py
argglobal
%argdel
$argadd ~/Desktop/zmp/side-work/client-project-scraper/
edit src/PricingRegister/lib/bq_manager.py
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
vsplit
wincmd _ | wincmd |
vsplit
2wincmd h
wincmd w
wincmd w
let &splitbelow = s:save_splitbelow
let &splitright = s:save_splitright
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe 'vert 1resize ' . ((&columns * 105 + 159) / 318)
exe 'vert 2resize ' . ((&columns * 106 + 159) / 318)
exe 'vert 3resize ' . ((&columns * 105 + 159) / 318)
tcd ~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister
argglobal
balt ~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister/lib/ssm_manager.py
setlocal fdm=syntax
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 47 - ((33 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 47
normal! 028|
wincmd w
argglobal
if bufexists(fnamemodify("~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister/global_settings.py", ":p")) | buffer ~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister/global_settings.py | else | edit ~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister/global_settings.py | endif
if &buftype ==# 'terminal'
  silent file ~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister/global_settings.py
endif
balt ~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister/lib/sns_manager.py
setlocal fdm=syntax
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=1
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 19 - ((18 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 19
normal! 032|
wincmd w
argglobal
if bufexists(fnamemodify("~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister/registers/printpac_multi_sticker_reg.py", ":p")) | buffer ~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister/registers/printpac_multi_sticker_reg.py | else | edit ~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister/registers/printpac_multi_sticker_reg.py | endif
if &buftype ==# 'terminal'
  silent file ~/Desktop/zmp/side-work/client-project-scraper/src/PricingRegister/registers/printpac_multi_sticker_reg.py
endif
balt ~/Desktop/zmp/side-work/client-project-scraper/src/readme.md
setlocal fdm=syntax
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 20 - ((19 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 20
normal! 02|
wincmd w
2wincmd w
exe 'vert 1resize ' . ((&columns * 105 + 159) / 318)
exe 'vert 2resize ' . ((&columns * 106 + 159) / 318)
exe 'vert 3resize ' . ((&columns * 105 + 159) / 318)
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=85
let &shortmess = s:shortmess_save
let &winminheight = s:save_winminheight
let &winminwidth = s:save_winminwidth
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
set hlsearch
nohlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
