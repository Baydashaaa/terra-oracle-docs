#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Документация: актуальные числа Oracle Score и время распределения казны.

Запускать из ~/terra-oracle-docs:
    python3 patch-docs-numbers.py
    grep -n "11571\|af9ad9eb\|21:00 UTC" index.html

ЧТО ПРАВИТСЯ

1. Code ID 11556 → 11571 (три места: бейдж, таблица, пример curl).
   Контракт мигрирован 15 августа на версию 0.8.0.

2. Контрольная сумма 8bec505d… → af9ad9eb7ad46700d29c56da97b42da27b4085c…
   Это сумма фактически развёрнутого WASM, сверенная на цепочке при
   миграции и совпавшая в rebel-2 и мейннете.

3. Распределение казны: среда 20:00 → 21:00 UTC. Расписание сдвинуто
   намеренно: в 20:00 работает розыгрыш и отправляет казне её долю, а
   распределение считает от баланса — одновременный запуск делал результат
   зависящим от того, кто успел первым.

4. Добавлена строка версии контракта в таблицу спецификации.

ЧТО НЕ ТРОГАЕТСЯ

Снимок 1,890 REP и его хеш e02fd7a5… оставлены как есть: они совпадают с
временной меткой в oracle-score-attest.js (2026-08-01T14:47:53). Расходится
с ними README самого контракта (1,780 REP, 4aed2576…) — устарел он, а не
документация. README править отдельно, в репозитории oracle-score.

Прочие упоминания 20:00 UTC в файле относятся к розыгрышам и верны — они
правиться не должны, поэтому замена времени привязана к строке про казну.
"""

import sys, io, os, shutil, datetime

SRC = 'index.html'

if not os.path.exists(SRC):
    sys.exit('не найден ' + SRC + ' — запускай из корня ~/terra-oracle-docs')

s = io.open(SRC, encoding='utf-8').read()

NEW_ID  = '11571'
NEW_SUM = 'af9ad9eb7ad46700d29c56da97b42da27b4085c270113cfd3a5bf21b6f72af58'
OLD_SUM = '8bec505dc36f6a414783ca956621eb3437fb6208b13381d06cc8dbeb6139238c'

if NEW_ID in s and OLD_SUM not in s:
    sys.exit('правка уже наложена — файл не тронут')

edits = []

edits.append(('<span class="badge">Code ID 11556</span>',
              '<span class="badge">Code ID %s</span>' % NEW_ID))

edits.append(('<tr><td>Code ID</td><td><code>11556</code></td></tr>',
              '<tr><td>Code ID</td><td><code>%s</code></td></tr>\n'
              '    <tr><td>Version</td><td><code>0.8.0</code></td></tr>' % NEW_ID))

edits.append(('<tr><td>Code checksum</td><td><code>%s</code></td></tr>' % OLD_SUM,
              '<tr><td>Code checksum</td><td><code>%s</code></td></tr>' % NEW_SUM))

edits.append(('curl -s https://terra-classic-lcd.publicnode.com/cosmwasm/wasm/v1/code/11556',
              'curl -s https://terra-classic-lcd.publicnode.com/cosmwasm/wasm/v1/code/%s' % NEW_ID))

# Время казны — привязка к строке именно про распределение, чтобы не задеть
# упоминания 20:00 UTC, относящиеся к розыгрышам
edits.append(('Distribution runs automatically every <strong>Wednesday at 20:00 UTC</strong> via GitHub Actions.',
              'Distribution runs automatically every <strong>Wednesday at 21:00 UTC</strong> via GitHub Actions '
              '&mdash; an hour after the draws, so the two never touch the treasury wallet at the same time.'))

for i, (old, new) in enumerate(edits, 1):
    n = s.count(old)
    if n != 1:
        sys.exit('замена %d: найдено %d совпадений вместо 1 — файл НЕ изменён' % (i, n))
    s = s.replace(old, new, 1)

# Ни одно упоминание 20:00 про розыгрыши не должно пострадать
draws_2000 = s.count('20:00 UTC')
if draws_2000 < 4:
    sys.exit('подозрительно мало упоминаний 20:00 UTC (%d) — файл НЕ изменён' % draws_2000)

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
shutil.copy(SRC, SRC + '.bak-' + stamp)
io.open(SRC, 'w', encoding='utf-8').write(s)

print('готово: %d замен' % len(edits))
print('упоминаний 20:00 UTC про розыгрыши осталось: %d (так и должно быть)' % draws_2000)
print('копия прежнего файла: %s.bak-%s' % (SRC, stamp))
