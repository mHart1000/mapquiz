import { Box, Container, Heading, Flex, Spacer, Button } from '@chakra-ui/react'
import { Link as RouterLink } from 'react-router-dom'

function Layout({ children }) {
  return (
    <Box bg="gray.50" minH="100vh">
      <Flex as="header" bg="blue.600" color="white" p={4} align="center">
        <Heading size="md">Map Quiz App</Heading>
        <Spacer />
        <Button as={RouterLink} to="/" colorScheme="whiteAlpha" variant="outline" size="sm">
          Home
        </Button>
      </Flex>

      <Container maxW="container.md" py={10}>
        {children}
      </Container>
    </Box>
  )
}

export default Layout
