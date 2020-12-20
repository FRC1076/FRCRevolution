
## ugly hack so that absolute references in submodules work
import os, sys
dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir}')

from .revbot import RevBot
# SPDX-License-Identifier: GPL-3.0-only
