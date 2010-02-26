from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from django.template import RequestContext#,Template
from django.utils import simplejson
from django.contrib.auth.decorators import login_required

from base.shortcuts import get_object_or_create

from jetpack.models import Jet, JetVersion, Cap, CapVersion
from jetpack.default_settings import settings

@login_required
def jetpack_edit(r, slug):
	"""
	Get jetpack and send it to item_edit
	"""
	jetpack = get_object_or_404(Jet, slug=slug)
	return item_edit(r, jetpack, "jetpack")
	

@login_required
def capability_edit(r, slug):
	"""
	Get capability and send it to item_edit
	"""
	capability = get_object_or_404(Cap, slug=slug)
	return item_edit(r, capability, "capability")
	

def item_edit(r, item, type):
	"""
	retrieve item and (if possible) version 
	Render the right edit page for the given type
	"""
	try:
		version = item.base_version
	except: 
		#valid, as newly created item has no version yet
		pass
	item_page = True
	jetpack_create_url = Jet.get_create_url()
	capability_create_url = Cap.get_create_url()
	return render_to_response("%s_edit.html" % type, locals(), 
				context_instance=RequestContext(r))
	

@login_required
def jetpack_version_edit(r, slug, version, counter):
	version = get_object_or_404(JetVersion, jetpack__slug=slug, name=version, counter=counter)
	item = version.jetpack
	type = "jetpack"
	return render_to_response('jetpack_edit.html', locals(), 
				context_instance=RequestContext(r))
	

@login_required
def capability_version_edit(r, slug, version, counter):
	version = get_object_or_404(CapVersion, capability__slug=slug, name=version, counter=counter)
	item = version.capability
	type = "capability"
	return render_to_response('capability_edit.html', locals(), 
				context_instance=RequestContext(r))


@login_required
def item_create(r, type):
	"""
	Create new item (Jetpack/Capability)
	This is a result of a popup window with just name and description
	Version will be saved in the item_version_create
	"""
	Klass = Jet if type=="jetpack" else Cap
	item = Klass(
		creator=r.user,
		name=r.POST.get("%s_name" % type),
		description=r.POST.get("%s_description" % type)
	)
	# TODO: validate
	item.save()
	return render_to_response("json/%s_created.json" % type, {type: item},
				context_instance=RequestContext(r),
				mimetype='application/json')
	


@login_required
def item_update(r, slug, type):
	"""
	Update the existing item's metadata only
	"""
	Klass = Jet if type=="jetpack" else Cap
	item = get_object_or_404(Klass, slug=slug)
	if not item.can_be_updated_by(r.user):
		return HttpResponseNotAllowed(HttpResponse(""))

	if '%s_description' % type in r.POST:
		item.description = r.POST.get('%s_description' % type)
	if '%s_public_permission' % type in r.POST:
		item.public_permission = r.POST.get('%s_public_permission' % type)
	if '%s_group_permission' % type in r.POST:
		item.group_permission = r.POST.get('%s_group_permission' % type)

	item.save()
	return render_to_response('json/%s_updated.json' % type, {type: item},
				context_instance=RequestContext(r),
				mimetype='application/json')

	
@login_required
def jetpack_version_create(r, slug):
	"""
	Save new version for the jetpack, get data from POST
	"""
	#TODO: save capabilities dependency
	jetpack = get_object_or_404(Jet, slug=slug)
	version_data = {
		"jetpack": jetpack,
		"author": r.user,
		"name": r.POST.get("version_name"),
		"manifest": r.POST.get("version_manifest"),
		"content": r.POST.get("version_content"),
		"description": r.POST.get("version_description"),
	}
	if "version_status" in r.POST:
		version_data["status"] = r.POST.get("version_status")
	if "version_published" in r.POST:
		version_data["published"] = r.POST.get("version_published")
	if "version_is_base" in r.POST:
		version_data["is_base"] = r.POST.get("version_is_base")
	version = JetVersion(**version_data)
	version.save()
	dep_capabilities = simplejson.loads(r.POST.get('capabilities','[]'));
	print dep_capabilities

	for c in dep_capabilities:
		dep_cap = CapVersion.objects.get(
						capability__slug=c['slug'],
						name=c['version'],
						counter=c['counter'])
		version.capabilities.add(dep_cap)

	return render_to_response('json/version_absolute_url.json', {'version': version},
				context_instance=RequestContext(r),
				mimetype='application/json')

@login_required
def jetpack_version_update(r, slug, version, counter):
	"""
	Update the given version - no counter change
	"""
	version = get_object_or_404(JetVersion, jetpack__slug=slug, name=version, counter=counter)
	# permission check
	if not version.author == r.user:
		return HttpResponseNotAllowed(HttpResponse(""))

	version.author = r.user
	version.name = r.POST.get("version_name", version.name)
	version.manifest = r.POST.get("version_manifest", version.manifest)
	version.content = r.POST.get("version_content", version.content)
	version.description = r.POST.get("version_description", version.description)
	version.status = r.POST.get("version_status", version.status)
	version.published =  r.POST.get("version_published", version.published)
	version.is_base = r.POST.get("version_is_base", version.is_base)
	version.save()
	return render_to_response('json/version_updated.json', {'version': version},
				context_instance=RequestContext(r),
				mimetype='application/json')
	
@login_required
def jetpack_version_save_as_base(r, slug, version, counter):
	"""
	Update the given version - no counter change
	"""
	version = get_object_or_404(JetVersion, jetpack__slug=slug, name=version, counter=counter)
	# permission check
	if not version.jetpack.can_be_updated_by(r.user):
		return HttpResponseNotAllowed(HttpResponse(""))

	version.is_base = True
	version.save()
	return render_to_response('json/version_saved_as_base.json', {'version': version},
				context_instance=RequestContext(r),
				mimetype='application/json')

	
@login_required
def capability_version_create(r, slug):
	"""
	save new version for the capability, get data from POST
	"""
	#TODO: save capabilities dependency
	capability = get_object_or_404(Cap, slug=slug)
	version_data = {
		"capability": capability,
		"author": r.user,
		"name": r.POST.get("version_name"),
		"content": r.POST.get("version_content"),
		"description": r.POST.get("version_description"),
	}
	if "version_status" in r.POST:
		version_data["status"] = r.POST.get("version_status")
	if "version_is_base" in r.POST:
		version_data["is_base"] = r.POST.get("version_is_base")
	version = CapVersion(**version_data)
	version.save()
	return render_to_response('json/version_absolute_url.json', {'version': version},
				context_instance=RequestContext(r),
				mimetype='application/json')

@login_required
def capability_version_update(r, slug, version, counter):
	"""
	Update the given version - no counter change
	"""
	version = get_object_or_404(CapVersion, capability__slug=slug, name=version, counter=counter)
	# permission check
	if not version.author == r.user:
		return HttpResponseNotAllowed(HttpResponse(""))

	version.author = r.user
	if "version_name" in r.POST:
		version.name = r.POST.get("version_name", version.name)
	version.content = r.POST.get("version_content", version.content)
	if "version_description" in r.POST:
		version.description = r.POST.get("version_description", version.description)
	version.status = r.POST.get("version_status", version.status)
	version.is_base = r.POST.get("version_is_base", version.is_base)
	version.save()
	return render_to_response('json/version_updated.json', {'version': version},
				context_instance=RequestContext(r),
				mimetype='application/json')
	
@login_required
def capability_version_save_as_base(r, slug, version, counter):
	"""
	Update the given version - no counter change
	"""
	version = get_object_or_404(CapVersion, capability__slug=slug, name=version, counter=counter)
	# permission check
	if not version.capability.can_be_updated_by(r.user):
		return HttpResponseNotAllowed(HttpResponse(""))

	version.is_base = True
	version.save()
	return render_to_response('json/version_saved_as_base.json', {'version': version},
				context_instance=RequestContext(r),
				mimetype='application/json')


def gallery(r, page=None):
	"""
	Display mixed list (Jetpacks with Capabilities)
	"""
	items = list(Jet.objects.all()[0:20])
	items.extend(list(Cap.objects.all()[0:20]))
	items = filter(lambda i: i.base_version, items)
	items.sort(lambda i, j: (j.base_version.last_update - i.base_version.last_update).seconds) 
	
	return render_to_response(
		'gallery.html', 
		locals(),
		context_instance=RequestContext(r))
	

@login_required
def capabilities_autocomplete(r):
	"""
	Display names of the modules (capabilities) which mark the pattern
	"""
	
@login_required
def add_dependency(r, slug, type, version=None, counter=None):
	"""
	Add dependency to the item represented by slug
	"""
	if type == 'jetpack':
		item = get_object_or_404(JetVersion, 
					jetpack__slug=slug, name=version, counter=counter)
	elif type == 'capability':
		item = get_object_or_404(CapVersion, 
					capability__slug=slug, name=version, counter=counter)

	dependency_slug = r.POST.get("dependency_slug")
	dependency_version = r.POST.get("dependency_version", None)
	dependency_counter = r.POST.get("dependency_counter", None)
	if dependency_version:
		dependency = CapVersion.objects.get(
						capability__slug=dependency_slug, 
						name=dependency_version, 
						counter=dependency_counter)
	else:
		cap = Cap.objects.get(slug=dependency_slug)
		dependency = cap.base_version

	item.capabilities.add(dependency)
	item.save()

	return render_to_response('json/dependency_added.json', {
					'item': item, 
					'version': dependency, 
					'cap': dependency.capability
				},
				context_instance=RequestContext(r),
				mimetype='application/json')
	
