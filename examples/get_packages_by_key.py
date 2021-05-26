from dnfdbus.client import DnfDbusClient

if __name__ == "__main__":
    client = DnfDbusClient()
    print(client.get_version())
    pkgs = client.get_packages_by_key("*qt6*")
    for pkg in pkgs:
        print(pkg)

    client.quit()
