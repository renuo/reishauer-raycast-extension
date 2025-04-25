import { ActionPanel, Detail, List, Action, Icon } from "@raycast/api";
import { useEffect, useState } from "react";

const API_URL = "http://192.168.100.154:5001/menu";

type MenuItem = {
  description: string;
  name: string;
  price: string;
};

function DetailsView(props: { item: MenuItem }) {
  const items = props.item.description.split(", ");
  const details = `
  # ${props.item.name}

  **Price**: ${props.item.price}

  ${items.map((item) => `- *${item}*`).join("\n")}
  `;

  return <Detail markdown={details} />;
}

export default function Command() {
  const [isLoading, setIsLoading] = useState(true);
  const [menu, setMenu] = useState<MenuItem[]>([]);

  useEffect(() => {
    const fetchMenu = async () => {
      setIsLoading(true); // Start loading
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const menuData = (await response.json()) as MenuItem[];
        setMenu(menuData);
      } catch (error) {
        console.error("Failed to fetch menu:", error);
        // Optionally, you could set an error state here and display it
        setMenu([]); // Clear menu on error
      } finally {
        setIsLoading(false); // Stop loading regardless of success or error
      }
    };

    fetchMenu();
  }, []);

  return (
    <List isLoading={isLoading}>
      {!isLoading && menu.length === 0 ? (
        <List.EmptyView title="No menu items found" description="Could not load menu from the server." />
      ) : (
        menu.map((item) => (
          <List.Item
            key={item.name} // Add a unique key prop
            icon={Icon.Bird}
            title={item.name}
            subtitle={item.price}
            actions={
              <ActionPanel>
                <Action.Push title="Show Details" target={<DetailsView item={item} />} />
              </ActionPanel>
            }
          />
        ))
      )}
    </List>
  );
}
