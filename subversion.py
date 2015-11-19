import sublime, sublime_plugin
import sys, os, pysvn

client = pysvn.Client();

wc_status_kind_map = {
pysvn.wc_status_kind.added: 'A',
pysvn.wc_status_kind.conflicted: 'C',
pysvn.wc_status_kind.deleted: 'D',
pysvn.wc_status_kind.external: 'X',
pysvn.wc_status_kind.ignored: 'I',
pysvn.wc_status_kind.incomplete: '!',
pysvn.wc_status_kind.missing: '!',
pysvn.wc_status_kind.merged: 'G',
pysvn.wc_status_kind.modified: 'M',
pysvn.wc_status_kind.none: ' ',
pysvn.wc_status_kind.normal: ' ',
pysvn.wc_status_kind.obstructed: '~',
pysvn.wc_status_kind.replaced: 'R',
pysvn.wc_status_kind.unversioned: '?',
}

def printSvnCmd(cmd,path):
	print("===================== svn %s %s =====================" % (cmd, path))

def showConsole(view):
	view.window().run_command('show_panel', args={'panel':'console'})


class SvndiffCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		file_name = self.view.file_name()

		if 'TEMP' in os.environ:
			tmpdir = os.environ['TEMP']
		elif 'TMPDIR' in os.environ:
			tmpdir = os.environ['TMPDIR']
		elif 'TMP' in os.environ:
			tmpdir = os.environ['TMP']
		elif os.path.exists( '/usr/tmp' ):
			tmpdir = '/usr/tmp'
		elif os.path.exists( '/tmp' ):
			tmpdir = '/tmp'
		else:
			print( 'No tmp dir!' )
			return

		revision1=pysvn.Revision( pysvn.opt_revision_kind.base )
		revision2=pysvn.Revision( pysvn.opt_revision_kind.working )

		showConsole(self.view)

		printSvnCmd("Diff", file_name)
		try:
			diff_text = client.diff( tmpdir, file_name, recurse=True, revision1=revision1, revision2=revision2, diff_options=['-u'])
		except pysvn.ClientError as e:
			print(e.args[0])
			return

		if len(diff_text) == 0:
			print("no Modified.")
		else:
			print( diff_text.replace( '\r\n', '\n' ) )


class SvnstCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		p_flag = 0
		paths = []


		if 'dirs' in args and args['dirs']:
			paths.extend(args['dirs'])
		elif 'files' in args and args['files']:
			paths.extend(args['files'])

		paths_str = ''.join(paths);
		all_files = client.status(paths_str, recurse=True, get_all=False, ignore=True, update=False);

		showConsole(self.view)
		printSvnCmd("Status", paths_str)
		all_files.sort(key=lambda x:x['text_status'] )
		for file in all_files:
			if file.text_status == pysvn.wc_status_kind.ignored and ignore:
				continue
			if file.text_status ==pysvn.wc_status_kind.normal:
				continue
			p_flag=1
			print( '%s\t%s' % (wc_status_kind_map[file.text_status], file.path))

		if p_flag == 0:
			print("no Changes.")

		print("\n")

class SvnciCommand(sublime_plugin.TextCommand):
	file_name=''
	view=None

	@staticmethod
	def on_cancel():
		printSvnCmd("Commit", SvnciCommand.file_name)
		print('Commit canceled.')

	@staticmethod
	def on_done(msg):

		showConsole(SvnciCommand.view)
		printSvnCmd("Commit", SvnciCommand.file_name)
		if len(msg) == 0 or msg.isspace():
			print("need commit message.")
			return

		print("Message:" + msg)

		try:
			commit_info = client.checkin( SvnciCommand.file_name, msg, recurse=False )
		except pysvn.ClientError as e:
			print(e.args[0])
			return

		rev = commit_info["revision"]

		if commit_info['post_commit_err'] is not None:
			print( commit_info['post_commit_err'])

		if rev is None:
			print( 'Nothing to commit' )
		elif rev.number > 0:
			print( 'Revision %s' % rev.number )
		else:
			print( 'Commit failed' )

	def run(self, edit, **args):
		SvnciCommand.view = self.view
		SvnciCommand.file_name = self.view.file_name()
		self.view.window().show_input_panel('SVN Commit Message:','', SvnciCommand.on_done, None, SvnciCommand.on_cancel)




