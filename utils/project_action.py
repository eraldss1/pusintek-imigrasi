import tableauserverclient as TSC
import time

from anytree import util, AnyNode, RenderTree
from utils.get_tableau_object_anytree import getTableauObject


def deleteAllProjects(server: TSC.Server, authentication: TSC.TableauAuth):
    with server.auth.sign_in(authentication):
        print("Formatting new server")

        with server.auth.sign_in(authentication):
            sites, pagination_item = server.sites.get()
            for site in sites:
                server.auth.switch_site(site)

                projects, pagination_item = server.projects.get()
                for project in projects:
                    if (project.parent_id == None and project.name != 'Default'):
                        server.projects.delete(project.id)

        print("New server formatted\n")
    time.sleep(5)


def createProject(server: TSC.Server, authentication: TSC.TableauAuth, project_node: AnyNode):
    source_site = util.commonancestors(project_node)[1]
    source_project_ancestor = util.commonancestors(project_node)
    source_project_ancestor = [x.name for x in source_project_ancestor][1:]

    print("Project to make:", project_node.name)

    with server.auth.sign_in(authentication):
        sites, site_pagination = server.sites.get()

        # Cari site di server baru
        target_site = None
        for site in sites:
            if site.name == source_site.name:
                target_site = site
                break
        server.auth.switch_site(target_site)
        print("Target site:", target_site.name)

        # if project_node.name == "default":
        #     print(project_node.parent_id)

        if not project_node.parent_id:
            if project_node.name.lower() != "default":
                new_project = TSC.ProjectItem(
                    name=project_node.name,
                )
                new_project = server.projects.create(new_project)
                print("Project created\n")
            else:
                print()

        else:
            req_options = TSC.RequestOptions()
            req_options.filter.add(
                TSC.Filter(
                    TSC.RequestOptions.Field.Name,
                    TSC.RequestOptions.Operator.Equals,
                    project_node.parent.name
                )
            )
            # print(project_node.parent.name)

            projects, pagination_item = server.projects.get(
                req_options=req_options,
            )
            target_project = projects[0]
            print("Target project:", target_project.id, "")

            new_project = TSC.ProjectItem(
                name=project_node.name,
                parent_id=target_project.id
            )
            new_project = server.projects.create(new_project)
            print("Project created\n")

        time.sleep(5)
