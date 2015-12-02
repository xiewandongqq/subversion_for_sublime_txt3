import sublime, sublime_plugin
import sys, os, time, threading
#sys.path.append(sublime.packages_path()+'/subversion')
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import pysvn

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

wc_notify_action_map = {
pysvn.wc_notify_action.add: 'A',
pysvn.wc_notify_action.commit_added: 'A',
pysvn.wc_notify_action.commit_deleted: 'D',
pysvn.wc_notify_action.commit_modified: 'M',
pysvn.wc_notify_action.commit_postfix_txdelta: None,
pysvn.wc_notify_action.commit_replaced: 'R',
pysvn.wc_notify_action.copy: 'c',
pysvn.wc_notify_action.delete: 'D',
pysvn.wc_notify_action.failed_revert: 'F',
pysvn.wc_notify_action.resolved: 'R',
pysvn.wc_notify_action.restore: 'R',
pysvn.wc_notify_action.revert: 'R',
pysvn.wc_notify_action.skip: 'skip',
pysvn.wc_notify_action.status_completed: None,
pysvn.wc_notify_action.status_external: 'X',
pysvn.wc_notify_action.update_add: 'A',
pysvn.wc_notify_action.update_completed: None,
pysvn.wc_notify_action.update_delete: 'D',
pysvn.wc_notify_action.update_external: 'X',
pysvn.wc_notify_action.update_update: 'U',
pysvn.wc_notify_action.annotate_revision: 'A',
}

# new in svn 1.4?
if hasattr( pysvn.wc_notify_action, 'locked' ):
    wc_notify_action_map[ pysvn.wc_notify_action.locked ] = 'locked'
    wc_notify_action_map[ pysvn.wc_notify_action.unlocked ] = 'unlocked'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_lock ] = 'failed_lock'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_unlock ] = 'failed_unlock'

# new in svn 1.5
if hasattr( pysvn.wc_notify_action, 'exists' ):
    wc_notify_action_map[ pysvn.wc_notify_action.exists ] = 'exists'
    wc_notify_action_map[ pysvn.wc_notify_action.changelist_set ] = 'changelist_set'
    wc_notify_action_map[ pysvn.wc_notify_action.changelist_clear ] = 'changelist_clear'
    wc_notify_action_map[ pysvn.wc_notify_action.changelist_moved ] = 'changelist_moved'
    wc_notify_action_map[ pysvn.wc_notify_action.foreign_merge_begin ] = 'foreign_merge_begin'
    wc_notify_action_map[ pysvn.wc_notify_action.merge_begin ] = 'merge_begin'
    wc_notify_action_map[ pysvn.wc_notify_action.update_replace ] = 'update_replace'

# new in svn 1.6
if hasattr( pysvn.wc_notify_action, 'property_added' ):
    wc_notify_action_map[ pysvn.wc_notify_action.property_added ] = 'property_added'
    wc_notify_action_map[ pysvn.wc_notify_action.property_modified ] = 'property_modified'
    wc_notify_action_map[ pysvn.wc_notify_action.property_deleted ] = 'property_deleted'
    wc_notify_action_map[ pysvn.wc_notify_action.property_deleted_nonexistent ] = 'property_deleted_nonexistent'
    wc_notify_action_map[ pysvn.wc_notify_action.revprop_set ] = 'revprop_set'
    wc_notify_action_map[ pysvn.wc_notify_action.revprop_deleted ] = 'revprop_deleted'
    wc_notify_action_map[ pysvn.wc_notify_action.merge_completed ] = 'merge_completed'
    wc_notify_action_map[ pysvn.wc_notify_action.tree_conflict ] = 'tree_conflict'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_external ] = 'failed_external'

# new in svn 1.7
if hasattr( pysvn.wc_notify_action, 'update_started' ):
    wc_notify_action_map[ pysvn.wc_notify_action.update_started ] = 'update_started'
    wc_notify_action_map[ pysvn.wc_notify_action.update_skip_obstruction ] = 'update_skip_obstruction'
    wc_notify_action_map[ pysvn.wc_notify_action.update_skip_working_only ] = 'update_skip_working_only'
    wc_notify_action_map[ pysvn.wc_notify_action.update_external_removed ] = 'update_external_removed'
    wc_notify_action_map[ pysvn.wc_notify_action.update_shadowed_add ] = 'update_shadowed_add'
    wc_notify_action_map[ pysvn.wc_notify_action.update_shadowed_update ] = 'update_shadowed_update'
    wc_notify_action_map[ pysvn.wc_notify_action.update_shadowed_delete ] = 'update_shadowed_delete'
    wc_notify_action_map[ pysvn.wc_notify_action.merge_record_info ] = 'merge_record_info'
    wc_notify_action_map[ pysvn.wc_notify_action.upgraded_path ] = 'upgraded_path'
    wc_notify_action_map[ pysvn.wc_notify_action.merge_record_info_begin ] = 'merge_record_info_begin'
    wc_notify_action_map[ pysvn.wc_notify_action.merge_elide_info ] = 'merge_elide_info'
    wc_notify_action_map[ pysvn.wc_notify_action.patch ] = 'patch'
    wc_notify_action_map[ pysvn.wc_notify_action.patch_applied_hunk ] = 'patch_applied_hunk'
    wc_notify_action_map[ pysvn.wc_notify_action.patch_rejected_hunk ] = 'patch_rejected_hunk'
    wc_notify_action_map[ pysvn.wc_notify_action.patch_hunk_already_applied ] = 'patch_hunk_already_applied'
    wc_notify_action_map[ pysvn.wc_notify_action.commit_copied ] = 'commit_copied'
    wc_notify_action_map[ pysvn.wc_notify_action.commit_copied_replaced ] = 'commit_copied_replaced'
    wc_notify_action_map[ pysvn.wc_notify_action.url_redirect ] = 'url_redirect'
    wc_notify_action_map[ pysvn.wc_notify_action.path_nonexistent ] = 'path_nonexistent'
    wc_notify_action_map[ pysvn.wc_notify_action.exclude ] = 'exclude'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_conflict ] = 'failed_conflict'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_missing ] = 'failed_missing'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_out_of_date ] = 'failed_out_of_date'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_no_parent ] = 'failed_no_parent'

# new in svn 1.7.1+?
if hasattr( pysvn.wc_notify_action, 'failed_locked' ):
    wc_notify_action_map[ pysvn.wc_notify_action.failed_locked ] = 'failed_locked'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_forbidden_by_server ] = 'failed_forbidden_by_server'
    wc_notify_action_map[ pysvn.wc_notify_action.skip_conflicted ] = 'skip_conflicted'

# new in svn 1.8
if hasattr( pysvn.wc_notify_action, 'update_broken_lock' ):
    wc_notify_action_map[ pysvn.wc_notify_action.update_broken_lock ] = 'update_broken_lock'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_obstruction ] = 'failed_obstruction'
    wc_notify_action_map[ pysvn.wc_notify_action.conflict_resolver_starting ] = 'conflict_resolver_starting'
    wc_notify_action_map[ pysvn.wc_notify_action.conflict_resolver_done ] = 'conflict_resolver_done'
    wc_notify_action_map[ pysvn.wc_notify_action.left_local_modifications ] = 'left_local_modifications'
    wc_notify_action_map[ pysvn.wc_notify_action.foreign_copy_begin ] = 'foreign_copy_begin'
    wc_notify_action_map[ pysvn.wc_notify_action.move_broken ] = 'move_broken'

# new in svn 1.9
if hasattr( pysvn.wc_notify_action, 'cleanup_external' ):
    wc_notify_action_map[ pysvn.wc_notify_action.cleanup_external ] = 'cleanup_external'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_requires_target ] = 'failed_requires_target'
    wc_notify_action_map[ pysvn.wc_notify_action.info_external ] = 'info_external'
    wc_notify_action_map[ pysvn.wc_notify_action.commit_finalizing ] = 'commit_finalizing'


def printSvnCmd(cmd,path):
	print("===================== svn %s %s =====================" % (cmd, path))

def showConsole(view):
	view.window().run_command('show_panel', args={'panel':'console'})

def getPath(view, args):
	path_str=''
	path=[]
	if 'dirs' in args and args['dirs']:
		path.extend(args['dirs'])
	elif 'files' in args and args['files']:
		path.extend(args['files'])

	if len(path) == 0:
		path.extend(view.file_name())

	return ''.join(path)



def fmtDateTime( t ):
    return time.strftime( '%d-%b-%Y %H:%M:%S', time.localtime( t ) )

def getTmpDir():
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
		tmpdir = ''
	return tmpdir		

class SvnoutputCommand(sublime_plugin.TextCommand):
	"""docstring for SvnoutputCommand"""
	def run(self, edit, **args):
		syntax_file = "Packages/Diff/Diff.tmLanguage"
		if 'syntax_file' in args and args['syntax_file']:
			syntax_file = args['syntax_file']
			
		if 'output' in args and args['output']:
			new_view = self.view.window().create_output_panel('svn_output')
			new_view.insert(edit, 0, args['output'])
			new_view.set_syntax_file(syntax_file)
			self.view.window().run_command('show_panel', args={'panel':'output.svn_output'})
	
class SvnOutput(object):
	"""docstring for SvnOutput"""

	def out_panel(self, output):
		self.view.run_command("svnoutput", args={"output":output})
			
	def progress_thread(self, target, title):
		self.status_bar_msg = title
		self.progress = False
		thread=threading.Thread(target=target)
		thread.start()
		thread2=threading.Thread(target=self.progress_bar)
		thread2.start()

	def progress_bar(self):
		status_pic = ['--', '\\', '|', '/']
		i=0
		while True:
			if(self.progress == True):
			 	break
			self.view.set_status("svn_status","%s working: %2s " %(self.status_bar_msg, status_pic[i%len(status_pic)]))
			time.sleep(0.1)
			i+=1
		self.view.set_status("svn_status","")	

class SvndiffCommand(sublime_plugin.TextCommand, SvnOutput):
	def run(self, edit,**args):


		path_str=getPath(self.view, args)
		tmpdir=getTmpDir()
		if(tmpdir == ''):
			print( 'No tmp dir!' )
			return

		revision1=pysvn.Revision( pysvn.opt_revision_kind.base )
		revision2=pysvn.Revision( pysvn.opt_revision_kind.working )


		try:
			diff_text = client.diff( tmpdir, path_str, recurse=True, revision1=revision1, revision2=revision2, diff_options=['-u'])
		except pysvn.ClientError as e:
			sublime.error_message(e.args[0])
			return

		if len(diff_text) == 0:
			self.out_panel("No changes.")
		else:
			self.out_panel(diff_text.replace('\r\n', '\n'))




class SvnstCommand(sublime_plugin.TextCommand, SvnOutput):
	def short_path(self, path, file_path):
		if os.path.isdir(path) :
			return file_path.split(path+'/')[1]
		else:
			return os.path.basename(file_path) 


	def run(self, edit, **args):

		self.paths_str = getPath(self.view, args)
		self.progress_thread(self.get_status, 'SVN status')

	def get_status(self):
		print_str=''
		p_flag = 0

		try:
			all_files = client.status(self.paths_str, recurse=True, get_all=False, ignore=True, update=False)
		except Exception as e:
			sublime.error_message(e.args[0])
			return

		all_files.sort(key=lambda x:x['text_status'] , reverse=True)
		for file in all_files:
			if file.text_status == pysvn.wc_status_kind.ignored:
				continue
			if file.text_status ==pysvn.wc_status_kind.normal:
				continue
			p_flag=1
			print_str += '\t%s\t\t%s\n' % (wc_status_kind_map[file.text_status], self.short_path(self.paths_str, file.path) )

		if p_flag == 0:
			print_str +="no Changes."

		print_str += "\n"
		self.out_panel( print_str)
		self.progress = True

class SvnciCommand(sublime_plugin.TextCommand):
	file_name=''
	view=None

	@staticmethod
	def on_cancel():
		printSvnCmd("Commit", SvnciCommand.file_name)
		print('Commit canceled.')

	@staticmethod
	def on_done(msg):

		# showConsole(SvnciCommand.view)
		printSvnCmd("Commit", SvnciCommand.file_name)
		if len(msg) == 0 or msg.isspace():
			sublime.message_dialog("Need commit message.")
			return


		try:
			commit_info = client.checkin( SvnciCommand.file_name, msg, recurse=True )
		except pysvn.ClientError as e:
			sublime.error_message(e.args[0])
			return

		# print(commit_info)

		rev = commit_info

		# if commit_info['post_commit_err'] is not None:
		# 	print( commit_info['post_commit_err'])

		if rev is None:
			sublime.message_dialog( 'Nothing to commit' )
		elif rev.number > 0:
			sublime.message_dialog( 'Revision %s' % rev.number +'\n Message:%s' % msg)
		else:
			sublime.message_dialog( 'Commit failed' )

	def run(self, edit, **args):
		SvnciCommand.view = self.view
		SvnciCommand.file_name = getPath(self.view, args);
		self.view.window().show_input_panel('SVN Commit Message:','', SvnciCommand.on_done, None, SvnciCommand.on_cancel)


class SvnupCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		path_str=''
		path=[]
		if 'dirs' in args and args['dirs']:
			path.extend(args['dirs'])
		elif 'files' in args and args['files']:
			path.extend(args['files'])

		if len(path) == 0:
			path.extend(self.view.file_name())

		path_str=''.join(path)

		print(path_str)
		
		printSvnCmd("Update",path_str)
		# showConsole(self.view)
		try:		
			rev_list = client.update( path_str, recurse=True )
		except pysvn.ClientError as e:
			sublime.error_message(e.args[0])
			return

		sublime.message_dialog('Revision number:%d' % rev_list[0].number)
		if type(rev_list) == type([]) and len(rev_list) != 1:
			print( 'rev_list = %r' % [rev.number for rev in rev_list] )
		
class SvnrevertCommand(sublime_plugin.TextCommand):
	"""docstring for SvnrevertCommand"""
	def run(self, edit, **args):
		paths_str=getPath(self.view, args)

		printSvnCmd("Revert", paths_str)
		

		try:
			client.revert(paths_str, True)
		except pysvn.ClientError as e:
			sublime.error_message(e.args[0])
			return

class SvnlogCommand(sublime_plugin.TextCommand, SvnOutput):
	def run(self, edit, **args):

		self.detail = False
		if 'detail' in args and args['detail']:
			self.detail = True

		self.paths_str=getPath(self.view, args)
		self.view.window().show_input_panel("SVN Log Range:", "500", self.on_done, None, None)

	def on_done(self, msg):
		self.msg = msg
		self.progress_thread(self.get_log, 'SVN log')


	def get_log(self):
		try:
			rev_range = int(self.msg)
			info = client.info(self.paths_str)
			start_revision= pysvn.Revision( pysvn.opt_revision_kind.number, info.revision.number - rev_range) 
			end_revision= pysvn.Revision( pysvn.opt_revision_kind.number, info.revision.number  ) 

			all_logs = client.log( self.paths_str,revision_start=start_revision,revision_end=end_revision,discover_changed_paths=True )
		except Exception as e:
			sublime.error_message(e.args[0])
			return	

		print_str= ''
		all_logs.reverse()
		for log in all_logs:
		    print_str+=( '-'*60 +'\n')
		    print_str+=( 'rev %d: %s | %s | %d lines' %
		        (log.revision.number
		        ,log.author
		        ,fmtDateTime( log.date )
		        ,len( log.message.split('\n') )) )

		    if len( log.changed_paths ) > 0:
		        print_str+=( '\nChanged paths:\n' )
		        for change_info in log.changed_paths:
		            if change_info.copyfrom_path is None:
		                print_str+=( '  %s %s\n' % (change_info.action, change_info.path) )
		            else:
		                print_str+=( '  %s %s (from %s:%d)\n' %
		                    (change_info.action
		                    ,change_info.path
		                    ,change_info.copyfrom_path
		                    ,change_info.copyfrom_revision.number) )

		    print_str+=( log.message + '\n')

		    if self.detail == True:
		    	print_str += '\n'
		    	print_str += self.getDiffText(log)

		print_str+=( '-'*60 + '\n')	
		self.out_panel( print_str )
		self.progress = True

	def getDiffText(self, log):

		ret_text=''
		tmpdir = getTmpDir()

		revision1 = pysvn.Revision(pysvn.opt_revision_kind.number, int(log.revision.number) - 1)
		revision2 = pysvn.Revision(pysvn.opt_revision_kind.number, log.revision.number)	
		diff_text = client.diff( tmpdir, self.view.file_name(), recurse=True, revision1=revision1, revision2=revision2, diff_options=['-u'])

		text_arr = diff_text.split('\n')
		for x in range(4):
			text_arr.pop(0)

		for t in text_arr:
			ret_text +=  t + '\n'
		return ret_text



class SvnaddCommand(sublime_plugin.TextCommand):
	"""docstring for SvnaddCommand"""
	def run(self, edit, **args):
		paths_str=getPath(self.view, args)
		try:
			client.add( paths_str, recurse=True, force=False )
		except pysvn.ClientError as e:
			sublime.error_message(e.args[0])
		
		