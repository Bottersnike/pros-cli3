import json

from click._termui_impl import ProgressBar as _click_ProgressBar

from .utils import *

_last_notify_value = 0
_current_notify_value = 0


def _machineoutput(obj: Dict[str, Any]):
    print(f'Uc&42BWAaQ{json.dumps(obj)}')


def _machine_notify(method: str, obj: Dict[str, Any], notify_value: Optional[int]):
    if notify_value is None:
        global _current_notify_value
        notify_value = _current_notify_value
    obj['type'] = f'notify/{method}'
    obj['notify_value'] = notify_value
    _machineoutput(obj)


def echo(text: str, err: bool = False, nl: bool = True, notify_value: int = None):
    if ismachineoutput():
        return _machine_notify('echo', {'text': text + ('\n' if nl else '')}, notify_value)
    else:
        return click.echo(text, nl=nl, err=err)


def confirm(text, default=False, abort=False, prompt_suffix=': ',
            show_default=True, err=False):
    if ismachineoutput():
        pass
    else:
        return click.confirm(text, default=default, abort=abort, prompt_suffix=prompt_suffix,
                             show_default=show_default, err=err)


def prompt(text, default=None, hide_input=False,
           confirmation_prompt=False, type=None,
           value_proc=None, prompt_suffix=': ',
           show_default=True, err=False):
    if ismachineoutput():
        # TODO
        pass
    else:
        return click.prompt(text, default=default, hide_input=hide_input, confirmation_prompt=confirmation_prompt,
                            type=type, value_proc=value_proc, prompt_suffix=prompt_suffix, show_default=show_default,
                            err=err)


def progressbar(iterable: Iterable = None, length: int = None, label: str = None, show_eta: bool = True,
                show_percent: bool = True, show_pos: bool = False, item_show_func: Callable = None,
                fill_char: str = '#', empty_char: str = '-', bar_template: str = '%(label)s [%(bar)s] %(info)s',
                info_sep: str = ' ', width: int = 36):
    if ismachineoutput():
        return _MachineOutputProgessBar(**locals())
    else:
        return click.progressbar(**locals())


class _MachineOutputProgessBar(_click_ProgressBar):
    def __init__(self, *args, **kwargs):
        global _current_notify_value
        kwargs['file'] = open(os.devnull, 'w')
        self.notify_value = kwargs.pop('notify_value', _current_notify_value)
        super(_MachineOutputProgessBar, self).__init__(*args, **kwargs)

    def __del__(self):
        self.file.close()

    def render_progress(self):
        super(_MachineOutputProgessBar, self).render_progress()
        obj = {'label': self.label, 'pct': self.pct}
        if self.show_eta and self.eta_known and not self.finished:
            obj['eta'] = self.eta
        _machine_notify('progress', obj, self.notify_value)


class Notification(object):
    def __init__(self, notify_value: Optional[int] = None):
        global _last_notify_value
        if not notify_value:
            notify_value = _last_notify_value + 1
        if notify_value > _last_notify_value:
            _last_notify_value = notify_value
        self.notify_value = notify_value
        self.old_notify_values = []

    def __enter__(self):
        global _current_notify_value
        self.old_notify_values.append(_current_notify_value)
        _current_notify_value = self.notify_value

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _current_notify_value
        _current_notify_value = self.old_notify_values.pop()
