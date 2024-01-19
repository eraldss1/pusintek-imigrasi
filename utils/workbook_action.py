import tableauserverclient as TSC
import os
import time

from anytree import util, AnyNode, findall, RenderTree
from utils.get_tableau_object_anytree import getTableauObject


def migrateWorkbook(
    server: TSC.Server,
    authentication: TSC.TableauAuth,
    workbook_node: AnyNode,
    file_path
):
    source_workbook = workbook_node

    source_site = util.commonancestors(source_workbook)[1]
    source_parent = source_workbook.parent
    source_parent_ancestor = util.commonancestors(source_parent)
    source_parent_ancestor = [x.name for x in source_parent_ancestor][1:]

    print("Source project path:", source_parent_ancestor)

    # New server object
    tree = AnyNode(type="Server", id="1", name="Server Baru")
    new_server_object = getTableauObject(server, authentication, tree)

    print("Workbook to migrate:", source_workbook.name)
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

        # Find target project in new server
        projects_in_new = findall(
            new_server_object,
            filter_=lambda node:
                node.name.lower() == source_parent.name.lower()
        )

        target_project = None
        for project in projects_in_new:
            project_ancestor = util.commonancestors(project)
            project_ancestor = [
                x.name for x in project_ancestor
            ][1:]

            if project_ancestor == source_parent_ancestor:
                target_project = project
                break

        print("Target project:", target_project.name)
        print("Target project id:", target_project.id)

        if target_project.name.lower() == "default":
            mode = "Overwrite"
        else:
            mode = "CreateNew"

        print("Publishing workbook")
        # Migrate workbook
        new_woorkbook = TSC.WorkbookItem(
            name=source_workbook.name,
            project_id=target_project.id
        )

        try:
            new_woorkbook = server.workbooks.publish(
                workbook_item=new_woorkbook,
                file=file_path,
                mode=mode,
                as_job=False,
                skip_connection_check=True
            )
            print('Workbook published\n')
        except:
            print("Publish failed\n")

        # Delete file
        os.remove(file_path)
        time.sleep(5)


def downloadWorkbook(server: TSC.Server, authentication: TSC.TableauAuth, workbook_node: AnyNode):
    with server.auth.sign_in(authentication):
        print(f'Downloading "{workbook_node.name}"')
        download_workbook = server.workbooks.download(
            workbook_node.id,
            filepath='temp/'
        )
        print(f'Downloaded "{download_workbook}"\n')
        time.sleep(3)

        return download_workbook
