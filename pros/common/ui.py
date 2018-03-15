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


def echo(text: str, err: bool = False, nl: bool = True, notify_value: int = None, color: Any = None, output_machine: bool = True):
    if ismachineoutput():
        if output_machine:
            return _machine_notify('echo', {'text': text + ('\n' if nl else '')}, notify_value)
    else:
        return click.echo(text, nl=nl, err=err, color=color)


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


def finalize(method: str, data: Union[str, Dict, object, List[Union[str, Dict, object, Tuple]]],
             human_prefix: Optional[str] = None):
    if isinstance(data, str):
        human_readable = data
    elif isinstance(data, dict):
        # TODO: something better than this
        human_readable = data
    elif isinstance(data, List):
        if isinstance(data[0], str):
            human_readable = '\n'.join(data)
        elif isinstance(data[0], dict) or isinstance(data[0], object):
            if not isinstance(data[0], dict):
                data = [d.__dict__ for d in data]
            import tabulate
            human_readable = tabulate.tabulate([d.values() for d in data], headers=data[0].keys())
        elif isinstance(data[0], tuple):
            import tabulate
            human_readable = tabulate.tabulate(data[1:], headers=data[0])
        else:
            human_readable = data
    elif hasattr(data, '__str__'):
        human_readable = str(data)
    else:
        # TODO: something better than this
        human_readable = data.__dict__
    human_readable = (human_prefix or '') + str(human_readable)
    if ismachineoutput():
        if hasattr(data, '__getstate__'):
            data = data.__getstate__()
        else:
            data = data.__dict__
        _machineoutput({
            'type': 'finalize',
            'method': method,
            'data': data,
            'human': human_readable
        })
    else:
        click.echo(human_readable)


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


class PROSLogFormatter(logging.Formatter):
    """
    A subclass of the logging.Formatter so that we can print full exception traces ONLY if we're in debug mode
    """

    def formatException(self, ei):
        if not isdebug():
            return '\n'.join(super().formatException(ei).split('\n')[-3:])
        else:
            return super().formatException(ei)


class PROSLogHandler(logging.StreamHandler):
    """
    A subclass of logging.StreamHandler so that we can correctly encapsulate logging messages
    """

    def emit(self, record):
        try:
            msg = self.format(record)
            if ismachineoutput():
                obj = {
                    'type': 'log/message',
                    'level': record.levelname,
                    'message': msg
                }
                msg = f'Uc&42BWAaQ{json.dumps(obj)}'
            stream = self.stream
            stream.write(msg)
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)
